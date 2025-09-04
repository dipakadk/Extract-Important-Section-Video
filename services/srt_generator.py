import os
import srt
from openai import OpenAI
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_srt_from_audio(input_audio_file: str,output_srt_file):
    with open(input_audio_file, "rb") as audio_file: 
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["segment"]
        )
        
        merged_segments = []
        current_segment = {"start": None, "end": None, "text": ""}

        for segment in transcript.segments:
            if current_segment["start"] is None:
                current_segment["start"] = segment.start
            
            if current_segment["text"]:
                current_segment["text"] += " " + segment.text.strip()
            else:
                current_segment["text"] = segment.text.strip()
            
            current_segment["end"] = segment.end

            if segment.text.strip().endswith("."):
                merged_segments.append(current_segment.copy())
                current_segment = {"start": None, "end": None, "text": ""}

        if current_segment["text"]:
            merged_segments.append(current_segment)

                
        srt_subtitles = []
        for i, segment in enumerate(merged_segments):
            start = timedelta(seconds=segment["start"])
            end = timedelta(seconds=segment["end"])
            subtitle = srt.Subtitle(index=i + 1, start=start, end=end, content=segment["text"])            
            srt_subtitles.append(subtitle)
            
        srt_content = srt.compose(srt_subtitles)
        try:
            with open(output_srt_file,"w",encoding="utf-8") as f:
                f.write(srt_content)
            print("SRT file generated successfully!!!!")
        except Exception as e:
            return f"Error while writing SRT file: {e}"