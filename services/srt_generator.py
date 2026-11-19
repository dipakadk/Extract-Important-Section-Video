import os
import srt
from datetime import timedelta


def _transcribe_with_openai(input_audio_file: str):
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv()
    api_key = os.getenv("OPENAI_STT_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Set OPENAI_STT_API_KEY or OPENAI_API_KEY to use OpenAI transcription.")

    client = OpenAI(api_key=api_key)
    with open(input_audio_file, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["segment"]
        )
    return transcript.segments


def _transcribe_with_local_whisper(input_audio_file: str):
    from faster_whisper import WhisperModel

    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(input_audio_file, vad_filter=True)
    return segments


def generate_srt_from_audio(
    input_audio_file: str,
    output_srt_file: str,
    transcription_provider: str = "openai",
):
    if transcription_provider == "openai":
        segments = _transcribe_with_openai(input_audio_file)
    elif transcription_provider == "local":
        segments = _transcribe_with_local_whisper(input_audio_file)
    else:
        raise ValueError(f"Unsupported transcription provider: {transcription_provider}")

    merged_segments = []
    current_segment = {"start": None, "end": None, "text": ""}

    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue
        if current_segment["start"] is None:
            current_segment["start"] = segment.start

        current_segment["text"] = f'{current_segment["text"]} {text}'.strip()
        current_segment["end"] = segment.end

        if text.endswith("."):
            merged_segments.append(current_segment.copy())
            current_segment = {"start": None, "end": None, "text": ""}

    if current_segment["text"]:
        merged_segments.append(current_segment)

    subtitles = [
        srt.Subtitle(
            index=index,
            start=timedelta(seconds=segment["start"]),
            end=timedelta(seconds=segment["end"]),
            content=segment["text"],
        )
        for index, segment in enumerate(merged_segments, start=1)
    ]
    with open(output_srt_file, "w", encoding="utf-8") as output_file:
        output_file.write(srt.compose(subtitles))