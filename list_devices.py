import pyaudiowpatch as pyaudio
with pyaudio.PyAudio() as p:
    for i in range(p.get_device_count()):
        d = p.get_device_info_by_index(i)
        if d['maxInputChannels'] > 0:
            print(d['index'], d['name'], 'channels:', d['maxInputChannels'])
