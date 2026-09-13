import numpy
import pyaudiowpatch as pyaudio

p = pyaudio.PyAudio()
cands = []
for i in range(p.get_device_count()):
    d = p.get_device_info_by_index(i)
    if d['maxInputChannels'] > 0 and '[Loopback]' not in d['name'] and 'b15' in d['name'].lower():
        cands.append((i, d['name'], d['maxInputChannels']))
for i in range(p.get_device_count()):
    d = p.get_device_info_by_index(i)
    if d['maxInputChannels'] > 0 and '[Loopback]' not in d['name'] and 'realtek' in d['name'].lower():
        cands.append((i, d['name'], d['maxInputChannels']))
print('CANDIDATES:')
for c in cands:
    print(' ', c)

RATE = 16000
CH = 1
SECONDS = 4
streams = {}
try:
    for i, name, ch in cands:
        try:
            streams[i] = p.open(format=pyaudio.paInt16, channels=CH, rate=RATE,
                                input=True, input_device_index=i, frames_per_buffer=1024)
            print('opened', i, name)
        except Exception as e:
            print('FAILED to open', i, name, '->', e)
    print('>>> SPEAK NOW into the headset (4 seconds)...')
    n = int(RATE / 1024 * SECONDS)
    rms = {i: 0.0 for i in streams}
    for _ in range(n):
        for i, s in streams.items():
            data = s.read(1024, exception_on_overflow=False)
            arr = numpy.frombuffer(data, dtype=numpy.int16)
            r = float(numpy.sqrt((arr.astype(float) ** 2).mean()))
            rms[i] = max(rms[i], r)
finally:
    for s in streams.values():
        s.stop_stream(); s.close()
p.terminate()

print('RESULTS (RMS per device):')
for i, name, ch in cands:
    if i in rms:
        tag = '  <== СЛУХАЄ ТЕБЕ' if rms[i] > 800 else ''
        print(f'  [{i}] {name} -> RMS {rms[i]:.0f}{tag}')
