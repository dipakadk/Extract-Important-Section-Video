import os
import warnings
warnings.filterwarnings("ignore")

from fastapi import FastAPI, UploadFile, File, HTTPException
from services import convert_mp4_to_mp3, generate_srt_from_audio
from moviepy import VideoFileClip, concatenate_videoclips
from services import filtering_section, time_to_seconds


srt_file_path = "srt_generation/generated_srt.srt"
final_output_dir = "FinalGenVideo"
os.makedirs(final_output_dir, exist_ok=True)
final_output = os.path.join(final_output_dir, "final_video.mp4")

app = FastAPI()


@app.post("/convert")
async def convert_video_to_audio(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        temp_file = f"temp_{file.filename}"
        with open(temp_file, "wb") as f:
            f.write(await file.read())

        # Convert to audio
        output_path = convert_mp4_to_mp3(
            temp_file,
            output_file_name=f"{os.path.splitext(file.filename)[0]}.mp3"
        )

        # Generate subtitles (writes to srt_file_path)
        generate_srt_from_audio(output_path, srt_file_path)
        print("✅ SRT file generated")

        # Prepare temp clip folder
        temp_clip_saving_loc = os.path.join("Video", "temp_clips")
        os.makedirs(temp_clip_saving_loc, exist_ok=True)

        # Clean old clips
        for filename in os.listdir(temp_clip_saving_loc):
            file_path = os.path.join(temp_clip_saving_loc, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
            except Exception as e:
                return {"error": f"Failed to delete {file_path}: {e}"}

        # Load video
        video_file = VideoFileClip(temp_file)

        # Extract subclips
        clips = []
        for i, sec in enumerate(filtering_section(srt_file_path)):
            start_time = time_to_seconds(sec.start_timestamp)
            end_time = time_to_seconds(sec.end_timestamp)

            if start_time is None or end_time is None:
                continue

            subclip = video_file.subclipped(start_time, end_time)  # ✅ fixed
            clips.append(subclip)

            # Save each clip separately (optional)
            clip_path = os.path.join(temp_clip_saving_loc, f"clip_{i}.mp4")
            subclip.write_videofile(clip_path, codec="libx264", audio_codec="aac")

        # Merge all subclips
        if clips:
            final_clip = concatenate_videoclips(clips)
            final_clip.write_videofile(final_output, codec="libx264", audio_codec="aac")
            final_clip.close()

        # Cleanup
        video_file.close()
        for clip in clips:
            clip.close()
        os.remove(temp_file)

        return {
            "message": "Your video has been successfully processed and only the important sections are saved.",
            "final_video": final_output,
            "audio_file": output_path
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
