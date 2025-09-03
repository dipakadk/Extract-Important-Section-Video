import os
import warnings
warnings.filterwarnings("ignore")
from moviepy import VideoFileClip
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydub import AudioSegment

print("success")