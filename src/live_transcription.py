import sounddevice as sd
from audio_check import list_devices
import time
from faster_whisper import WhisperModel
from numpy import concatenate
import threading
import queue

buffer = []
buffer_queue = queue.Queue()

def input_stream():
    input_stream = sd.InputStream(samplerate=16000,blocksize=4000,device=list_devices("input")[1],channels=1,dtype="float32",latency='low',callback=callback)
    input_stream.start()
    return input_stream

def callback(indata, frames, time, status):
    # print(f"Size: {indata.shape}")
    # print(f"Frames: {frames}")

    global buffer
    buffer.append(indata.copy())

    # print(len(buffer)*frames)
    # if(len(buffer)*frames <= 48000):
    #     print("Buffer pending")
    # else:
    #     print("Buffer sent")
    #     buffer = [indata]
    
    if(len(buffer)*frames >= 48000):
        buffer_queue.put(buffer)
        buffer = [indata.copy()]

def live_transcription(model):
    while True:
        buffer = buffer_queue.get()
        buffer_to_transcripte = concatenate(buffer).flatten()

        segments, info = model.transcribe(buffer_to_transcripte, beam_size=5)

        transcription_text = ""
        for segment in segments:
            transcription_text += segment.text

        print(transcription_text)

if __name__ == "__main__":
    print("Model loading")
    model = WhisperModel("base", device="cpu", compute_type="float32")
    print("Model loaded")

    input_stream_thread = threading.Thread(target=input_stream)
    live_transcription_thread = threading.Thread(target=live_transcription,args=(model,))

    print("Live transcription starting")

    input_stream_thread.start()
    live_transcription_thread.start()