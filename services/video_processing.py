import os

from moviepy import VideoFileClip, concatenate_videoclips

from .formatting import filtering_section, time_to_seconds
from .srt_generator import generate_srt_from_audio
from .video_to_audio import convert_mp4_to_mp3


def process_video(
    input_video_path,
    work_dir,
    final_video_path=None,
    transcription_provider="openai",
    llm_provider="openai",
    ollama_model=None,
):
    os.makedirs(work_dir, exist_ok=True)
    audio_dir = os.path.join(work_dir, "audio")
    srt_path = os.path.join(work_dir, "generated_srt.srt")
    output_path = final_video_path or os.path.join(work_dir, "final_video.mp4")

    audio_path = convert_mp4_to_mp3(
        input_video_path,
        output_folder=audio_dir,
        output_file_name="source_audio.mp3",
    )
    generate_srt_from_audio(audio_path, srt_path, transcription_provider)

    video = VideoFileClip(input_video_path)
    clips = []
    final_clip = None
    try:
        for section in filtering_section(srt_path, llm_provider, ollama_model, video.duration):
            start_time = time_to_seconds(section.start_timestamp)
            end_time = time_to_seconds(section.end_timestamp)
            clips.append(video.subclipped(start_time, end_time))

        if not clips:
            raise ValueError("No important sections were found in this video.")

        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=os.path.join(work_dir, "temp-audio.m4a"),
            remove_temp=True,
            logger=None,
        )
    finally:
        if final_clip is not None:
            final_clip.close()
        for clip in clips:
            clip.close()
        video.close()

    return {"final_video": output_path, "audio_file": audio_path}