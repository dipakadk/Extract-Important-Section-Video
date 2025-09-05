import os
import warnings
warnings.filterwarnings("ignore")
from fastapi import FastAPI,UploadFile, File, HTTPException
from services import convert_mp4_to_mp3,generate_srt_from_audio
from moviepy import VideoFileClip

srt_file_path = "srt_generation/generated_srt.srt"

app = FastAPI()

@app.post("/convert")
async def convert_video_to_audio(file: UploadFile = File(...)):
    try:
        temp_file = f"temp_{file.filename}"
        with open(temp_file, "wb") as f:
            f.write(await file.read())

        output_path = convert_mp4_to_mp3(
            temp_file,
            output_file_name=f"{os.path.splitext(file.filename)[0]}.mp3"
        )
        os.remove(temp_file)
        srt = generate_srt_from_audio(output_path,srt_file_path)
        
        temp_clip_saving_loc = os.path.join("Video", "temp_clips")
        os.makedirs(temp_clip_saving_loc, exist_ok=True)
        
        for filename in os.listdir(temp_clip_saving_loc):
            file_path = os.path.join(temp_clip_saving_loc, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path) 
            except Exception as e:
                return f"Failed to delete {file_path}: {e}"

        
        video_file = VideoFileClip(file)
        
        clip = []
        # for i,sec in enumerate()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        return "transcript"

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
