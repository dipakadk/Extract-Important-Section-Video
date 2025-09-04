import os
import warnings
warnings.filterwarnings("ignore")
from fastapi import FastAPI,UploadFile, File, HTTPException
from services import convert_mp4_to_mp3,generate_srt_from_audio
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
        transcript = generate_srt_from_audio(output_path,srt_file_path)
        return transcript

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
