import generation_utils
import re
import os
from moviepy.editor import *

def make_movie(title, music_title):
    folder_name = generation_utils.title_to_filename(title) 

    if not os.path.exists(os.path.join("projects", folder_name)):
        print(f"Project folder with name {title} does not exist!")
        return

    voice_path = os.path.join("projects",folder_name,folder_name + ".aiff")
    if not os.path.exists(voice_path):
        voice_path = os.path.join("projects",folder_name,folder_name + ".mp3")
    music_path = os.path.join("music",music_title + ".mp3")
    images_path = os.path.join("projects",folder_name,"images")
    voice = AudioFileClip(voice_path)
    music = AudioFileClip(music_path)
    music.volumex(0.1)
    voice.set_start(0)
    voice_length = voice.duration
    music.set_start(0)

    audio_file = CompositeAudioClip([voice, music])

    sentences = generation_utils.load_script(os.path.join("projects",folder_name, folder_name + ".txt"))

    clips = []

    wpm = int(os.getenv('WPM'))
    current_time = 0

    for i in range(len(sentences)):
        USING_VIDEO = False
        file_name = os.path.join(images_path, str(i) + ".jpg")
        if not os.path.exists(file_name):
            file_name = os.path.join(images_path, str(i) + ".jpeg")
        if not os.path.exists(file_name):
            file_name = os.path.join(images_path, str(i) + ".png")
        if not os.path.exists(file_name):
            file_name = os.path.join(images_path, str(i) + ".gif")
        if not os.path.exists(file_name):
            file_name = os.path.join(images_path, str(i) + ".mp4")
            USING_VIDEO = True
        print(f"Creating clip for {file_name}")
        if not USING_VIDEO:
            clip = ImageClip(file_name).set_start(current_time).resize((1080, 720))
        else:
            clip = VideoFileClip(file_name).set_start(current_time).resize((1080, 720))
        duration = generation_utils.number_of_words(sentences[i]) / wpm * 60
        current_time += duration
        clip.duration = duration
        clips.append(clip)

    if len(clips) > 1:
        video = CompositeVideoClip(clips, use_bgclip = True)
    else:
        video = clips[0]
        
    audio_file.duration = max(current_time, voice_length)
    video.audio = audio_file
    video.duration = max(current_time, voice_length)
    video.write_videofile(os.path.join("projects",folder_name, folder_name + ".mp4"), fps=24, audio=True, audio_codec='aac', preset='ultrafast',logger='bar', threads = 6)