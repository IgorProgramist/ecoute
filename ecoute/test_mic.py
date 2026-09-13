import wave, os
import pyaudiowpatch as pyaudio
import numpy
import config
from faster_whisper import WhisperModel
import torch

pattern = config.MIC_DEVICE_NAME.strip().lower()
p = pyaudio.PyAudio()
cands = []
for i in range(p.get_device_count()):
    d = p.get_device_info_by_index(i)
    if d['maxInputChannels'] > 0 and '[Loopback]' not in d['name'] and pattern in d['name'].lower():
        cands.append((i, d['name']))
print('CANDIDATES:', cands)

RATE = 16000
CHUNK = 1024
SECONDS = 5

# проба: 1.5с міряємо RMS на кожному кандидаті, обираємо хто реально чує
PROBE_SECONDS = 1.5
print('>>> PROBE: say something short...')
import time
for t in range(3, 0, -1):
    print(f'  probe in {t}...')
    time.sleep(1)
probe_frames = int(RATE / CHUNK * PROBE_SECONDS)
streams = {}
for i, name in cands:
    try:
        streams[i] = p.open(format=pyaudio.paInt16, channels=1, rate=RATE,
                            input=True, input_device_index=i, frames_per_buffer=CHUNK)
    except Exception as e:
        print('probe skip', i, name, '->', e)
print('>>> PROBE: say something short (1.5s)...')
rms = {i: 0.0 for i in streams}
for _ in range(probe_frames):
    for i, s in streams.items():
        data = s.read(CHUNK, exception_on_overflow=False)
        arr = numpy.frombuffer(data, dtype=numpy.int16)
        r = float(numpy.sqrt((arr.astype(float) ** 2).mean()))
        rms[i] = max(rms[i], r)
for s in streams.values():
    s.stop_stream(); s.close()
for i, name in cands:
    if i in rms:
        print(f'  probe [{i}] {name} -> RMS {rms[i]:.0f}')
idx = max(rms, key=lambda k: rms[k])
print('PICKED:', idx, dict(cands)[idx])

print('>>> SPEAK NOW (5 seconds)...')
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, input_device_index=idx, frames_per_buffer=CHUNK)
frames = []
for _ in range(int(RATE / CHUNK * SECONDS)):
    frames.append(stream.read(CHUNK, exception_on_overflow=False))
stream.stop_stream()
stream.close()
p.terminate()

data = b''.join(frames)
arr = numpy.frombuffer(data, dtype=numpy.int16)
print('MAX amplitude:', arr.max(), '| RMS:', round(float(numpy.sqrt((arr.astype(float)**2).mean())),1), '(max ~32767)')

wf = wave.open('mic_test.wav', 'wb')
wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(RATE)
wf.writeframes(data); wf.close()
print('saved mic_test.wav, transcribing...')

m = WhisperModel(config.WHISPER_MODEL, device='cuda' if torch.cuda.is_available() else 'cpu',
                 compute_type='float32' if torch.cuda.is_available() else 'int8')
segs, _ = m.transcribe('mic_test.wav', language='en', vad_filter=True)
print('TRANSCRIPT:', ' '.join(s.text for s in segs))
