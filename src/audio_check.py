import sounddevice as sd

def list_inputs():
    devices = sd.query_devices()
    inputs=[]
    hostapis = sd.query_hostapis()
    default_index = -1
    for i,device in enumerate(devices):
        if device['max_input_channels'] > 0 and hostapis[device['hostapi']]['name'] != 'Windows WDM-KS':
            if sd.default.device[0] == i:
                default_index=device['index']
                inputs.append((device['index'], device['name'] + " (default)"))
            else:
                inputs.append((device['index'], device['name']))
    print("Available audio input devices:")
    for index, name in inputs:
        print(f"  {index}: {name}")
    if not inputs:
        raise RuntimeError("No audio input device detected.")
    if default_index == -1:
        raise RuntimeError("No audio output device detected.")
    return inputs, default_index

def list_outputs():
    devices = sd.query_devices()
    outputs=[]
    hostapis = sd.query_hostapis()
    default_index = -1
    for i,device in enumerate(devices):
        if device['max_output_channels'] > 0 and hostapis[device['hostapi']]['name'] != 'Windows WDM-KS':
            if sd.default.device[1] == i:
                default_index=device['index']
                outputs.append((device['index'], device['name'] + " (default)"))
            else:
                outputs.append((device['index'], device['name']))
    print("Available audio output devices:")
    for index, name in outputs:
        print(f"  {index}: {name}")
    if not outputs:
        raise RuntimeError("No audio output device detected.")
    if default_index == -1:
        raise RuntimeError("No audio output device detected.")
    return outputs, default_index

def record_audio(input_index,duration=5,samplerate=16000):
    frames = duration*samplerate
    print("Start of recording")
    audio=sd.rec(frames,samplerate,channels=1,dtype='float32',device=input_index)
    sd.wait()
    print("End of recording")
    return audio

list_inputs()
list_outputs()

input_index = int(input("Selected Audio Input Device: "))
output_index = int(input("Selected Audio Output Device: "))

sd.play(data=record_audio(input_index),samplerate=16000,device=output_index)
print("Listening to the recording")
sd.wait()