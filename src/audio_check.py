import sounddevice as sd

def list_devices(mode):
    if mode == "input":
        channel_key = 'max_input_channels'
        default_position = 0
        label = "input"
    elif mode == "output":
        channel_key = 'max_output_channels'
        default_position = 1
        label = "output"

    devices = sd.query_devices()
    hostapis = sd.query_hostapis()
    results = []
    default_index = -1

    for i, device in enumerate(devices):
        if device[channel_key] > 0 and hostapis[device['hostapi']]['name'] != 'Windows WDM-KS':
            if sd.default.device[default_position] == i:
                default_index = device['index']
                results.append((device['index'], device['name'] + " (default)"))
            else:
                results.append((device['index'], device['name']))

    print(f"Available audio {label} devices:")
    for index, name in results:
        print(f"  {index}: {name}")

    if not results:
        raise RuntimeError(f"No audio {label} device detected.")
    if default_index == -1:
        raise RuntimeError(f"No default audio {label} device detected.")

    return results, default_index

def record_audio(input_index,duration=5,samplerate=16000):
    frames = duration*samplerate
    print("Start of recording")
    audio=sd.rec(frames,samplerate,channels=1,dtype='float32',device=input_index)
    sd.wait()
    print("End of recording")
    return audio

if __name__ == "__main__":
    list_devices("input")
    input_index = int(input("Selected Audio Input Device: "))

    list_devices("output")
    output_index = int(input("Selected Audio Output Device: "))

    sd.play(data=record_audio(input_index), samplerate=16000, device=output_index)
    print("Listening to the recording")
    sd.wait()