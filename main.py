import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from services import process_video



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
final_output_dir = os.path.join(BASE_DIR, "FinalGenVideo")
os.makedirs(final_output_dir, exist_ok=True)
final_output = os.path.join(final_output_dir, "final_video.mp4")


app = FastAPI()


@app.post("/convert")
async def convert_video_to_audio(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename or "video.mp4")[1] or ".mp4"
        with tempfile.NamedTemporaryFile(dir=BASE_DIR, suffix=suffix, delete=False) as temp_file:
            temp_file.write(await file.read())
            temp_path = temp_file.name

        result = process_video(temp_path, BASE_DIR, final_output)
        return {
            "message": "Your video has been successfully processed and only the important sections are saved.",
            **result,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "temp_path" in locals() and os.path.exists(temp_path):
            os.remove(temp_path)