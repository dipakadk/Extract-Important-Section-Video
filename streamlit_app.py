import os
import tempfile
from glob import glob
from urllib.parse import urlparse

import streamlit as st
import yt_dlp

from services import process_video


YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be", "www.youtu.be"}
SUPPORTED_VIDEO_EXTENSIONS = [
    "mp4", "mov", "mkv", "webm", "avi", "mpeg", "mpg", "wmv", "flv",
    "m4v", "3gp", "ts", "mts", "m2ts", "ogv", "asf", "vob",
]

st.set_page_config(page_title="Video Highlights", page_icon="V", layout="centered")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { --ink: #172524; --muted: #64736f; --green: #237a61; --paper: #f5f7f2; }
    .stApp { background: radial-gradient(ellipse at 82% 4%, #dcece0 0, transparent 34%), var(--paper); color: var(--ink); }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: 0; color: var(--ink); }
    .block-container { max-width: 860px; padding-top: 3rem; padding-bottom: 4rem; }
    .eyebrow { color: var(--green); font-size: .78rem; font-weight: 700; text-transform: uppercase; letter-spacing: .12em; }
    .intro { color: var(--muted); font-size: 1.05rem; margin-top: -.5rem; }
    div[data-testid="stFileUploader"], div[data-testid="stTextInput"] { background: rgba(255,255,255,.72); border-radius: 8px; }
    [data-testid="stWidgetLabel"] p, [data-testid="stRadio"] label p { color: var(--ink) !important; }
    [data-testid="stFileUploaderDropzone"] { background: #fff !important; border: 1px dashed #9aaca4 !important; }
    [data-testid="stFileUploaderDropzone"] button { color: var(--ink) !important; background: #f5f7f2 !important; }
    [data-testid="stFileUploaderDropzone"] div, [data-testid="stFileUploaderDropzone"] span { color: var(--muted) !important; }
    div.stButton > button { background: var(--green); color: white; border: 0; border-radius: 6px; font-weight: 700; min-height: 2.8rem; }
    div.stButton > button:hover { background: #185e4a; color: white; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="eyebrow">Video tools / Highlights</div>', unsafe_allow_html=True)
st.title("Find the moments that matter.")
st.markdown('<p class="intro">Upload a video or paste a YouTube link. The same transcription and highlight workflow runs on either source.</p>', unsafe_allow_html=True)

source_type = st.radio("Video source", ["Upload a video", "YouTube link"], horizontal=True)
uploaded_file = None
youtube_url = ""

if source_type == "Upload a video":
    uploaded_file = st.file_uploader("Choose a video", type=SUPPORTED_VIDEO_EXTENSIONS)
else:
    youtube_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Create highlight video", type="primary", use_container_width=True):
    if source_type == "Upload a video" and uploaded_file is None:
        st.error("Choose a video file to continue.")
    elif source_type == "YouTube link" and not youtube_url.strip():
        st.error("Paste a YouTube URL to continue.")
    else:
        with st.spinner("Processing video. Transcription and highlight selection can take a few minutes..."):
            try:
                with tempfile.TemporaryDirectory(prefix="video-highlights-") as work_dir:
                    if uploaded_file is not None:
                        input_path = os.path.join(work_dir, os.path.basename(uploaded_file.name))
                        with open(input_path, "wb") as video_file:
                            video_file.write(uploaded_file.getbuffer())
                    else:
                        parsed_url = urlparse(youtube_url.strip())
                        if parsed_url.scheme not in {"http", "https"} or parsed_url.hostname not in YOUTUBE_HOSTS:
                            raise ValueError("Enter a valid YouTube URL.")
                        download_template = os.path.join(work_dir, "source.%(ext)s")
                        options = {
                            "format": "best[ext=mp4]/best",
                            "outtmpl": download_template,
                            "quiet": True,
                            "no_warnings": True,
                        }
                        with yt_dlp.YoutubeDL(options) as downloader:
                            downloader.download([youtube_url.strip()])
                        downloaded_files = glob(os.path.join(work_dir, "source.*"))
                        downloaded_files = [path for path in downloaded_files if not path.endswith(".part")]
                        if not downloaded_files:
                            raise ValueError("YouTube did not provide a downloadable video file.")
                        input_path = downloaded_files[0]

                    result = process_video(input_path, work_dir)
                    with open(result["final_video"], "rb") as final_video:
                        video_bytes = final_video.read()

                st.success("Your highlight video is ready.")
                st.video(video_bytes)
                st.download_button(
                    "Download highlight video",
                    data=video_bytes,
                    file_name="video_highlights.mp4",
                    mime="video/mp4",
                    use_container_width=True,
                )
            except Exception as error:
                st.error(f"Video processing failed: {error}")