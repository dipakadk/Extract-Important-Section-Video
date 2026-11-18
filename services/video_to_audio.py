import os
from moviepy import VideoFileClip


def create_folder_and_file(folder_name= "audio",file_name = "audio_file.mp3"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder {folder_name} is created.")
    file_path = os.path.join(folder_name,file_name)
    return file_path
    
def convert_mp4_to_mp3(input_file:str,output_folder="audio",output_file_name="convered_mp3_file.mp3"):
    output_file_path = create_folder_and_file(output_folder,output_file_name)
    video = VideoFileClip(input_file)
    try:
        if video.audio is None:
            raise ValueError("The uploaded video does not contain an audio track.")
        video.audio.write_audiofile(
            output_file_path,
            fps=44100,
            codec="libmp3lame",
            logger=None,
        )
    finally:
        video.close()
    return output_file_path
    
    
