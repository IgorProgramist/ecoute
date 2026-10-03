import os
import sys
import glob

def _add_cuda_dll_dirs():
    # faster-whisper (CTranslate2) потребує власні CUDA DLLs, torch-івські не підходять
    base = os.path.join(os.path.dirname(sys.executable), "..", "..", "Roaming", "Python", "Python313", "site-packages", "nvidia")
    for pattern in [os.path.join(base, "cublas", "bin"), os.path.join(base, "cudnn", "bin")]:
        pattern = os.path.normpath(pattern)
        if os.path.isdir(pattern):
            os.add_dll_directory(pattern)
    # fallback: пошук через pip-пакети незалежно від розташування
    try:
        import importlib.util
        for pkg in ("nvidia.cublas", "nvidia.cudnn"):
            spec = importlib.util.find_spec(pkg.replace(".", "\\") if False else pkg)
            if spec and spec.submodule_search_locations:
                bin_dir = os.path.join(list(spec.submodule_search_locations)[0], "bin")
                if os.path.isdir(bin_dir):
                    os.add_dll_directory(bin_dir)
                    # CTranslate2 грузить cublas64_12.dll звичайним LoadLibrary —
                    # той шукає по PATH і ігнорує add_dll_directory
                    os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]
    except Exception:
        pass

from faster_whisper import WhisperModel
from openai import OpenAI
import config

def get_model(use_api):
    if use_api:
        return APIWhisperTranscriber()
    else:
        return FasterWhisperTranscriber()

def _has_cuda():
    # без torch: CTranslate2 сам знає CUDA (torch на 2.5GB не потрібен)
    try:
        import ctranslate2
        return ctranslate2.get_cuda_device_count() > 0
    except Exception:
        return False

class FasterWhisperTranscriber:
    def __init__(self):
        print(f"[INFO] Loading Faster Whisper model ({config.WHISPER_MODEL})...")
        _add_cuda_dll_dirs()
        device = "cuda" if _has_cuda() else "cpu"
        try:
            self.model = WhisperModel(config.WHISPER_MODEL, device=device, compute_type="int8")
            # тестовий прогін: CUDA DLLs можуть бути відсутні — дізнаємось одразу
            import numpy as _np
            import faster_whisper as _fw
            _dummy = _np.zeros((80, 3000), dtype=_np.float32)
            self.model.encode(_dummy)
            print(f"[INFO] Faster Whisper using {device.upper()}")
        except Exception as e:
            print(f"[WARN] {device.upper()} failed ({e}), falling back to CPU")
            device = "cpu"
            self.model = WhisperModel(config.WHISPER_MODEL, device=device, compute_type="int8")
            print("[INFO] Faster Whisper using CPU")
        self.device = device

    def get_transcription(self, wav_file_path):
        try:
            lang = config.TRANSCRIBE_LANGUAGE
            language = lang if lang in ("en", "uk") else None
            segments, _ = self.model.transcribe(wav_file_path, beam_size=config.BEAM_SIZE, language=language,
                                                vad_filter=True, without_timestamps=True,
                                                initial_prompt=getattr(config, "WHISPER_PROMPT", "") or None)
            full_text = " ".join(segment.text for segment in segments)
            return full_text.strip()
        except Exception as e:
            print(e)
            return ''

class APIWhisperTranscriber:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key)

    def get_transcription(self, wav_file_path):
        try:
            with open(wav_file_path, "rb") as audio_file:
                result = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return result.text.strip()
        except Exception as e:
            print(e)
            return ''
