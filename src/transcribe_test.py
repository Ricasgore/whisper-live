from faster_whisper import WhisperModel
import time
import jiwer
import pandas as pd

MODEL_SIZES = [
    "tiny",
    "base",
    "small",
    "medium"
]

def test_model(model_size,sample_name):
    print(f"Testing {model_size} model")
    #print(f"Model: {model_size}")

    loading_start_time = time.time()

    model = WhisperModel(model_size, device="cpu", compute_type="float32")

    loading_end_time = time.time()
    loading_time = loading_end_time - loading_start_time

    #print(f"Loading time: {loading_time:.2f}s")

    transcription_start_time = time.time()

    segments, info = model.transcribe(f"data/{sample_name}", beam_size=5)

    #print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    transcription_text = ""
    for segment in segments:
        transcription_text += segment.text

    transcription_end_time = time.time()
    transcription_time = transcription_end_time - transcription_start_time

    #print(f"Transcription time: {transcription_time:.2f}s")

    with open("data/subtitles_bbc_news.txt", "r", encoding="utf-8") as f:
        reference_text = f.read()

    wer = jiwer.wer(transcription_text,reference_text)
    #print(f"Word Error Rate (WER): {wer*100:.2f}%")

    standardized_wer = jiwer.wer(
        reference_text,
        transcription_text,
        reference_transform=jiwer.wer_standardize, #WARNING: ExpandCommonEnglishContractions()
        hypothesis_transform=jiwer.wer_standardize #WARNING: ExpandCommonEnglishContractions()
    )
    #print(f"StandardizeD WER: {standardized_wer*100:.2f}%")
    
    data = {"model_size": model_size, "loading_time (s)": round(loading_time,2), "transcription_time (s)": round(transcription_time,2), "wer (%)": round(wer*100,2), "standardized war (%)": round(standardized_wer*100,2)}

    return data, transcription_text

if __name__ == "__main__":
    data_list = []
    for model_size in MODEL_SIZES:
        data_list.append(test_model(model_size,"sample_en_bbc_news.wav")[0])
    data_frame = pd.DataFrame(data_list)
    print(data_frame) 