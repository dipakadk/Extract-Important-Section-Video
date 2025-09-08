import os
import warnings
warnings.filterwarnings("ignore")
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from services import convert_mp4_to_mp3, generate_srt_from_audio
from moviepy import VideoFileClip, concatenate_videoclips
from services import filtering_section, time_to_seconds



# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
srt_file_path = os.path.join(BASE_DIR, "srt_generation", "generated_srt.srt")
final_output_dir = os.path.join(BASE_DIR, "FinalGenVideo")
os.makedirs(final_output_dir, exist_ok=True)
final_output = os.path.join(final_output_dir, "final_video.mp4")


app = FastAPI()


@app.post("/convert")
async def convert_video_to_audio(file: UploadFile = File(...)):
    try:
        temp_file = os.path.join(BASE_DIR, f"temp_{file.filename}")
        with open(temp_file, "wb") as f:
            f.write(await file.read())

        output_path = convert_mp4_to_mp3(
            temp_file,
            output_file_name=f"{os.path.splitext(file.filename)[0]}.mp3"
        )

        generate_srt_from_audio(output_path, srt_file_path)

        temp_clip_saving_loc = os.path.join(BASE_DIR, "Video", "temp_clips")
        os.makedirs(temp_clip_saving_loc, exist_ok=True)

        for filename in os.listdir(temp_clip_saving_loc):
            file_path = os.path.join(temp_clip_saving_loc, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
            except Exception as e:
                return {"error": f"Failed to delete {file_path}: {e}"}

        video_file = VideoFileClip(temp_file)

        clips = []
        for i, sec in enumerate(filtering_section(srt_file_path)):
            start_time = time_to_seconds(sec.start_timestamp)
            end_time = time_to_seconds(sec.end_timestamp)

            if start_time is None or end_time is None:
                continue

            subclip = video_file.subclipped(start_time, end_time)
            clips.append(subclip)

            clip_path = os.path.join(temp_clip_saving_loc, f"clip_{i}.mp4")
            subclip.write_videofile(
                clip_path,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile=f"temp-audio-{i}.m4a",
                remove_temp=True
            )

        if clips:
            final_clip = concatenate_videoclips(clips)
            final_clip.write_videofile(
                final_output,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True
            )
            final_clip.close()

        video_file.close()
        for clip in clips:
            clip.close()
        os.remove(temp_file)
        
        if os.path.exists(temp_clip_saving_loc):
            shutil.rmtree(temp_clip_saving_loc)

        return {
            "message": "Your video has been successfully processed and only the important sections are saved.",
            "final_video": final_output,
            "audio_file": output_path
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))