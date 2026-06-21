import sounddevice as sd
from audio_check import list_devices
import time
from faster_whisper import WhisperModel
from numpy import concatenate
import threading
import queue
import torch
from silero_vad import load_silero_vad, VADIterator

LANGUAGE = "fr"
MODEL_SIZE = "small"

buffer = []
buffer_queue = queue.Queue()

vad_model = load_silero_vad()
vad_iterator = VADIterator(vad_model, sampling_rate=16000)

speech_started = False

def input_stream():
    stream = sd.InputStream(samplerate=16000,blocksize=512,device=list_devices("input")[1],channels=1,dtype="float32",latency='low',callback=callback)
    stream.start()
    return stream

def callback(indata, frames, time, status):
    # print(f"Size: {indata.shape}")
    # print(f"Frames: {frames}")

    global buffer , speech_started
    
    chunk = indata.copy().flatten()
    chunk_tensor = torch.from_numpy(chunk)

    speech_dict = vad_iterator(chunk, return_seconds=True)

    if speech_dict and "start" in speech_dict:
        speech_started = True
        buffer = [chunk]
    elif speech_started:
        buffer.append(chunk)

    if speech_dict and "end" in speech_dict:
        speech_started = False
        if buffer:
            buffer_queue.put(buffer)
        buffer = []

def live_transcription(model):
    while True:
        buffer = buffer_queue.get()
        buffer_to_transcripte = concatenate(buffer).flatten()

        segments, info = model.transcribe(buffer_to_transcripte, beam_size=5, language=LANGUAGE, condition_on_previous_text=False)

        transcription_text = ""
        for segment in segments:
            transcription_text += segment.text

        print(transcription_text)

if __name__ == "__main__":
    print("Model loading")
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="float32")
    print("Model loaded")

    input_stream_thread = threading.Thread(target=input_stream)
    live_transcription_thread = threading.Thread(target=live_transcription,args=(model,))

    print("Live transcription starting")

    input_stream_thread.start()
    live_transcription_thread.start()