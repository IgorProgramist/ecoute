import custom_speech_recognition as sr
import pyaudiowpatch as pyaudio
from datetime import datetime
import numpy
import config

RECORD_TIMEOUT = 1.5
ENERGY_THRESHOLD = 250
DYNAMIC_ENERGY_THRESHOLD = True

class BaseRecorder:
    def __init__(self, source):
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = ENERGY_THRESHOLD
        self.recorder.dynamic_energy_threshold = DYNAMIC_ENERGY_THRESHOLD
        self.recorder.pause_threshold = 0.35
        self.recorder.non_speaking_duration = 0.25

        if source is None:
            raise ValueError("audio source can't be None")

        self.source = source

    def adjust_for_noise(self, device_name, msg):
        print(f"[INFO] Adjusting for ambient noise from {device_name}. " + msg)
        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)
        print(f"[INFO] Completed ambient noise adjustment for {device_name}.")

    def record_into_queue(self, audio_queue):
        def record_callback(_, audio:sr.AudioData) -> None:
            data = audio.get_raw_data()
            audio_queue.put((data, datetime.utcnow()))

        self.recorder.listen_in_background(self.source, record_callback, phrase_time_limit=RECORD_TIMEOUT)

class DefaultMicRecorder(BaseRecorder):
    def __init__(self):
        mic_index = self._find_mic()
        if mic_index is not None:
            print(f"[INFO] Using configured mic device index {mic_index}")
            source = sr.Microphone(device_index=mic_index, sample_rate=16000)
        else:
            print("[INFO] Using default Windows microphone")
            source = sr.Microphone(sample_rate=16000)
        super().__init__(source=source)
        self.adjust_for_noise("Default Mic", "Please make some noise from the Default Mic...")

    @staticmethod
    def _find_mic():
        pattern = config.MIC_DEVICE_NAME.strip().lower()
        if not pattern:
            return None
        matches = []
        with pyaudio.PyAudio() as p:
            for i in range(p.get_device_count()):
                d = p.get_device_info_by_index(i)
                if d['maxInputChannels'] > 0 and "[Loopback]" not in d['name'] \
                        and pattern in d['name'].lower():
                    matches.append((i, d))
            if not matches:
                print(f"[WARN] Mic device matching '{pattern}' not found, using default")
                return None
            print(f"[INFO] Mic candidates: {[(i, d['name'], d['maxInputChannels']) for i, d in matches]}")
            if config.MIC_AUTO_PICK and len(matches) > 1:
                best_i = DefaultMicRecorder._pick_by_rms(p, matches)
                if best_i is not None:
                    return best_i
            # fallback: ендпоінт з найбільшим числом каналів
            matches.sort(key=lambda m: (m[1]['maxInputChannels'], -m[0]), reverse=True)
            best_i, best_d = matches[0]
            return best_i

    @staticmethod
    def _pick_by_rms(p, matches):
        # коротка проба: кожен кандидат пише 1.5с, обираємо хто реально чує
        RATE = 16000
        CHUNK = 1024
        SECONDS = 1.5
        frames_needed = int(RATE / CHUNK * SECONDS)
        streams = {}
        for i, d in matches:
            try:
                streams[i] = p.open(format=pyaudio.paInt16, channels=1, rate=RATE,
                                    input=True, input_device_index=i,
                                    frames_per_buffer=CHUNK)
            except Exception as e:
                print(f"[INFO] Probe skip [{i}] {d['name']} -> {e}")
        if not streams:
            return None
        import time
        print("[INFO] Mic probe: say something short...")
        for t in range(3, 0, -1):
            print(f"[INFO]   probe in {t}...")
            time.sleep(1)
        rms = {i: 0.0 for i in streams}
        try:
            for _ in range(frames_needed):
                for i, s in streams.items():
                    data = s.read(CHUNK, exception_on_overflow=False)
                    arr = numpy.frombuffer(data, dtype=numpy.int16)
                    r = float(numpy.sqrt((arr.astype(numpy.float64) ** 2).mean()))
                    rms[i] = max(rms[i], r)
        finally:
            for s in streams.values():
                try:
                    s.stop_stream()
                    s.close()
                except Exception:
                    pass
        for i, d in matches:
            if i in rms:
                print(f"[INFO] Probe [{i}] {d['name']} -> RMS {rms[i]:.0f}")
        best_i = max(rms, key=lambda k: rms[k])
        if rms[best_i] < 200:
            print("[WARN] Probe: all candidates quiet, falling back to channel heuristic")
            return None
        print(f"[INFO] Probe picked device [{best_i}] {dict((i, d['name']) for i, d in matches)[best_i]}")
        return best_i

class DefaultSpeakerRecorder(BaseRecorder):
    def __init__(self):
        with pyaudio.PyAudio() as p:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            
            if not default_speakers["isLoopbackDevice"]:
                for loopback in p.get_loopback_device_info_generator():
                    if default_speakers["name"] in loopback["name"]:
                        default_speakers = loopback
                        break
                else:
                    print("[ERROR] No loopback device found.")
        
        source = sr.Microphone(speaker=True,
                               device_index= default_speakers["index"],
                               sample_rate=int(default_speakers["defaultSampleRate"]),
                               chunk_size=1024,
                               channels=default_speakers["maxInputChannels"])
        super().__init__(source=source)
        self.adjust_for_noise("Default Speaker", "Please make or play some noise from the Default Speaker...")