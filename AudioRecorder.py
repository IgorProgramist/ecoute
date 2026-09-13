import custom_speech_recognition as sr
import pyaudiowpatch as pyaudio
from datetime import datetime
import config

RECORD_TIMEOUT = 3
ENERGY_THRESHOLD = 1000
DYNAMIC_ENERGY_THRESHOLD = False

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
        with pyaudio.PyAudio() as p:
            for i in range(p.get_device_count()):
                d = p.get_device_info_by_index(i)
                if d['maxInputChannels'] > 0 and "[Loopback]" not in d['name'] \
                        and pattern in d['name'].lower():
                    return i
        print(f"[WARN] Mic device matching '{pattern}' not found, using default")
        return None

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
                               chunk_size=pyaudio.get_sample_size(pyaudio.paInt16),
                               channels=default_speakers["maxInputChannels"])
        super().__init__(source=source)
        self.adjust_for_noise("Default Speaker", "Please make or play some noise from the Default Speaker...")