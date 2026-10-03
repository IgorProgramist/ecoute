import wave
import os
import threading
import tempfile
import custom_speech_recognition as sr
import io
import numpy
from datetime import datetime, timedelta
import pyaudiowpatch as pyaudio
from heapq import merge
import config

PHRASE_TIMEOUT = 3.05
MAX_PHRASES = 10

class AudioTranscriber:
    def __init__(self, mic_source, speaker_source, model):
        self.transcript_data = {"You": [], "Speaker": []}
        self.speaker_buffer = ""   # монотонний буфер питання
        self.buffer_epoch = 0      # номер відстрілу
        # буфер = завершені фрази + ПОТОЧНА фраза. Поточну whisper щоразу
        # розпізнає з початку (last_sample накопичується), тому її текст
        # ЗАМІНЮЄМО, а не дописуємо — інакше питання повторюється 2-4 рази
        self._speaker_done = ""
        self._speaker_current = ""
        self._buffer_phrase_id = 0
        self._drop_speaker_audio = False
        self.transcript_changed_event = threading.Event()
        self.audio_model = model
        self.audio_sources = {
            "You": {
                "sample_rate": mic_source.SAMPLE_RATE,
                "sample_width": mic_source.SAMPLE_WIDTH,
                "channels": mic_source.channels,
                "last_sample": bytes(),
                "last_spoken": None,
                "new_phrase": True,
                "phrase_text": "",
                "phrase_epoch": 0,
                "process_data_func": self.process_mic_data
            },
            "Speaker": {
                "sample_rate": speaker_source.SAMPLE_RATE,
                "sample_width": speaker_source.SAMPLE_WIDTH,
                "channels": speaker_source.channels,
                "last_sample": bytes(),
                "last_spoken": None,
                "new_phrase": True,
                "phrase_text": "",
                "phrase_epoch": 0,
                "process_data_func": self.process_speaker_data
            }
        }

    def transcribe_audio_queue(self, speaker_queue, mic_queue):
        import queue
        
        while True:
            pending_transcriptions = []
            
            mic_data = []
            while True:
                try:
                    data, time_spoken = mic_queue.get_nowait()
                    self.update_last_sample_and_phrase_status("You", data, time_spoken)
                    mic_data.append((data, time_spoken))
                except queue.Empty:
                    break
                    
            speaker_data = []
            while True:
                try:
                    data, time_spoken = speaker_queue.get_nowait()
                    self.update_last_sample_and_phrase_status("Speaker", data, time_spoken)
                    speaker_data.append((data, time_spoken))
                except queue.Empty:
                    break
            
            if mic_data:
                source_info = self.audio_sources["You"]
                try:
                    fd, path = tempfile.mkstemp(suffix=".wav")
                    os.close(fd)
                    source_info["process_data_func"](source_info["last_sample"], path)
                    text = self.audio_model.get_transcription(path)
                    if text != '' and text.lower() != 'you':
                        latest_time = max(time for _, time in mic_data)
                        pending_transcriptions.append(("You", text, latest_time))
                except Exception as e:
                    print(f"Transcription error for You: {e}")
                finally:
                    os.unlink(path)
                    source_info["last_sample"] = bytes()
            
            if speaker_data:
                source_info = self.audio_sources["Speaker"]
                try:
                    print(f"[TRANS] speaker: {len(speaker_data)} chunks, {len(source_info['last_sample'])} bytes")
                    fd, path = tempfile.mkstemp(suffix=".wav")
                    os.close(fd)
                    source_info["process_data_func"](source_info["last_sample"], path)
                    text = self.audio_model.get_transcription(path)
                    print(f"[TRANS] result: {text[:80]!r}")
                    if text != '' and text.lower() != 'you':
                        latest_time = max(time for _, time in speaker_data)
                        pending_transcriptions.append(("Speaker", text, latest_time))
                except Exception as e:
                    print(f"Transcription error for Speaker: {e}")
                finally:
                    os.unlink(path)
            
            if pending_transcriptions:
                pending_transcriptions.sort(key=lambda x: x[2])
                for who_spoke, text, time_spoken in pending_transcriptions:
                    self.update_transcript(who_spoke, text, time_spoken)
                
                self.transcript_changed_event.set()
            
            threading.Event().wait(0.1)

    def update_last_sample_and_phrase_status(self, who_spoke, data, time_spoken):
        source_info = self.audio_sources[who_spoke]
        dropped = who_spoke == "Speaker" and self._drop_speaker_audio
        if dropped:
            self._drop_speaker_audio = False
        if dropped or (source_info["last_spoken"] and time_spoken - source_info["last_spoken"] > timedelta(seconds=PHRASE_TIMEOUT)):
            source_info["last_sample"] = bytes()
            source_info["new_phrase"] = True
            # лічильник, а не прапорець: кілька шматків за один прохід черги
            # перетирали new_phrase останнім значенням
            source_info["phrase_epoch"] += 1
        else:
            source_info["new_phrase"] = False

        # зберігаємо ts і довжину ПОПЕРЕДНЬОГО шматка (для розрахунку
        # реальної паузи в аудіо між шматками)
        source_info["prev_spoken"] = source_info["last_spoken"]
        source_info["prev_data_len"] = source_info.get("last_data_len", 0)

        source_info["last_sample"] += data
        source_info["last_spoken"] = time_spoken
        source_info["last_data_len"] = len(data)

    def process_mic_data(self, data, temp_file_name):
        audio_data = sr.AudioData(data, self.audio_sources["You"]["sample_rate"], self.audio_sources["You"]["sample_width"])
        wav_data = self._amplify_wav_bytes(audio_data.get_wav_data(), config.MIC_GAIN)
        with open(temp_file_name, 'w+b') as f:
            f.write(wav_data)

    def _amplify_wav_bytes(self, wav_bytes, gain):
        if not gain or gain <= 1.0:
            return wav_bytes
        buf = io.BytesIO(wav_bytes)
        with wave.open(buf, 'rb') as r:
            params = r.getparams()
            frames = r.readframes(r.getnframes())
        arr = numpy.frombuffer(frames, dtype=numpy.int16).astype(numpy.float32) * gain
        arr = numpy.clip(arr, -32767, 32767).astype(numpy.int16)
        out = io.BytesIO()
        with wave.open(out, 'wb') as w:
            w.setparams(params)
            w.writeframes(arr.tobytes())
        return out.getvalue()

    def process_speaker_data(self, data, temp_file_name):
        with wave.open(temp_file_name, 'wb') as wf:
            wf.setnchannels(self.audio_sources["Speaker"]["channels"])
            p = pyaudio.PyAudio()
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.audio_sources["Speaker"]["sample_rate"])
            wf.writeframes(data)

    def update_transcript(self, who_spoke, text, time_spoken):
        source_info = self.audio_sources[who_spoke]
        transcript = self.transcript_data[who_spoke]

        if who_spoke == "Speaker":
            # ОДИН монотонний буфер: питання НЕ розбивається на під-питання.
            # Все почуте з минулого відстрілу дописується сюди.
            if source_info["phrase_epoch"] != self._buffer_phrase_id:
                # почалась нова фраза: попередня завершена, зберігаємо її
                self._buffer_phrase_id = source_info["phrase_epoch"]
                self._speaker_done = (self._speaker_done + " " + self._speaker_current).strip()
            self._speaker_current = text
            if len(self._speaker_done) > 4000:
                self._speaker_done = self._speaker_done[-2000:]
            self.speaker_buffer = (self._speaker_done + " " + self._speaker_current).strip()

        if source_info["new_phrase"] or len(transcript) == 0:
            if len(transcript) > MAX_PHRASES:
                transcript.pop(-1)
            transcript.insert(0, (f"{who_spoke}: [{text}]\n\n", time_spoken))
        else:
            transcript[0] = (f"{who_spoke}: [{text}]\n\n", time_spoken)

    def clear_speaker_buffer(self):
        """Викликається після відстрілу відповіді: далі буфер з чистого."""
        self.speaker_buffer = ""
        self._speaker_done = ""
        self._speaker_current = ""
        # аудіо вже відданого питання не має потрапити в наступне
        self._drop_speaker_audio = True
        self.buffer_epoch += 1

    def get_current_speaker_phrase(self):
        """Повний накопичений текст питання (все з минулого відстрілу)."""
        return self.speaker_buffer.strip()

    def get_speaker_phrase_epoch(self):
        """Номер відстрілу: змінюється щоразу, коли буфер очищено."""
        return self.buffer_epoch

    def get_speaker_last_ts(self):
        """Час останнього АУДІО-шматка спікера — сигнал 'інтерв'юер ще говорить'."""
        return self.audio_sources["Speaker"]["last_spoken"]

    def get_transcript(self):
        combined_transcript = list(merge(
            self.transcript_data["You"], self.transcript_data["Speaker"], 
            key=lambda x: x[1], reverse=True))
        combined_transcript = combined_transcript[:MAX_PHRASES]
        return "".join([t[0] for t in combined_transcript])

    def get_recent_you_text(self, window_seconds=12):
        cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)
        parts = [text for text, ts in self.transcript_data["You"] if ts >= cutoff]
        return "".join(parts)

    def get_latest_speaker_ts(self):
        if self.transcript_data["Speaker"]:
            return self.transcript_data["Speaker"][0][1]
        return None
    
    def clear_transcript_data(self):
        self.transcript_data["You"].clear()
        self.transcript_data["Speaker"].clear()

        self.audio_sources["You"]["last_sample"] = bytes()
        self.audio_sources["Speaker"]["last_sample"] = bytes()

        self.audio_sources["You"]["new_phrase"] = True
        self.audio_sources["Speaker"]["new_phrase"] = True

        self.speaker_buffer = ""
        self._speaker_done = ""
        self._speaker_current = ""