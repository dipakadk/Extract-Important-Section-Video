
# Extract Only Important Sections from Video

This project extracts the **most important sections** from a given video. The final output is a shortened video containing only the key highlights.

## Features
- Input a video (MP4 format)  
- Convert video to audio (MP3 format)  
- Transcribe audio using **OpenAI Whisper**  
- Generate subtitle (`.srt`) files  
- Use **LLM (OpenAI)** to analyze transcripts  
- Extract important sections with timestamps  
- Generate short clips of important sections  
- Merge clips into a final highlight video  

## Workflow

```mermaid
flowchart LR
    A["Input Video (MP4 Format)"] --> B["Convert Video to Audio (MP3 Format)"]
    B --> C["Audio Transcription (OpenAI Whisper Model)"]
    C --> D["Generate SRT File"]
    D --> E["LLM (OpenAI)"]
    E --> F["Extract Important Topics & Sections with Timestamps"]
    F --> G["Generate Important Section-wise Video Clip"]
    G --> H["Merge Video Clips"]
    H --> I["Output (MP4 Format)"]
````

## Project Structure

```
EXTRACTIMPVIDEO/
│── audio/                  # Extracted audio files
│   └── final_video.mp3
│
│── chains/                 # Chains for processing
│   ├── generate_topic_chain.py
│   ├── important_section_chain.py
│
│── FinalGenVideo/          # Final generated video
│   └── final_video.mp4
│
│── llm_models/             # LLM schemas and configs
│   └── chat_model_schema.py
│
│── services/               # Core services
│   ├── formatting.py
│   ├── get_section.py
│   ├── srt_generator.py
│   ├── video_to_audio.py
│
│── srt_generation/         # Generated subtitle files
│   └── generated_srt.srt
│
│── .env.example            # Example env file
│── main.py                 # Main entry point
│── pyproject.toml          # Project dependencies (uv)
│── requirements.txt        # Python dependencies
│── README.md               # Documentation
```

---

## Installation

This project uses **uv** for package management.

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/extractimpvideo.git
   cd extractimpvideo
   ```

2. Install dependencies:

   ```bash
   uv add -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and add your **OpenAI API key**:

   ```bash
   OPENAI_STT_API_KEY=your_api_key_here
   OPENAI_API_KEY=your_api_key_here
   ```

---

## Usage

Start the FastAPI server with:

```bash
uv run uvicorn main:app --reload
```

* Input: Original video (`.mp4`)
* Output: Highlighted video (`.mp4`) will be generated and saved in the specified path.

---

## Dependencies

* [OpenAI Whisper](https://github.com/openai/whisper) – Speech-to-text
* [OpenAI GPT Models](https://platform.openai.com/) – LLM for summarization
* [MoviePy](https://zulko.github.io/moviepy/) – Video editing
* [FFmpeg](https://ffmpeg.org/) – Audio & video conversion

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
