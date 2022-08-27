print("Launching VidGen...")
import PySimpleGUI as sg
print("Talking to the internet...")
import generation_utils
import re
import os
import platform
from movie_maker import make_movie
import fakeyou
import uberduck
print("Done set up, time to generate!")

sg.theme('SystemDefaultForReal')   # Add a touch of color

on_mac = platform.system() == 'Darwin'

prompt_types = {}

promptsFile = open('prompts.txt', 'r')
for line in promptsFile.readlines():
    prompt = line.split(";")
    prompt_types[prompt[0]] = prompt[1]
promptsFile.close()

google_voices = generation_utils.get_US_google_cloud_voice_names()
fakeyou_voices = [] #fakeyou.get_all_model_names()

uberduck_voices = []
if uberduck.valid():
    uberduck_voices += uberduck.get_all_model_names()
uberduck_voices.sort()

voices = ["Default"] + ["-- GOOGLE VOICES --"] + google_voices + ["-- FAKEYOU VOICES --"] + fakeyou_voices + ["-- UBERDUCK VOICES --"] + uberduck_voices

music_files = []

for filename in os.listdir("music"):
    f = os.path.join("music", filename)
    if os.path.isfile(f) and filename.endswith("mp3"):
        music_files.append(os.path.basename(f).replace(".mp3",""))

logo_image = sg.Image(filename="logo.png")

# All the stuff inside your window.
layout = [
            [sg.Text('Enter video topic/title: '), sg.InputText(key='title')],
            [sg.Text('Prompt Type'), sg.Combo(list(prompt_types.keys()),default_value='Video Essay',key='promptType')],
            [sg.Text('Background Music'), sg.Combo(music_files,default_value='chill',key='music'),sg.Text('TTS Voice'), sg.Combo(voices,default_value='Default',key='voice')],
            [sg.Text('Media Method'), sg.Combo(["Pexels", "Storyblocks", "Just Images"],default_value='Pexels',key='mediaMethod')],
            [sg.Text("1."), sg.Button('Generate Resources'), sg.Text("2."), sg.Button('Create Movie')],
            [sg.Text("Extra Options:")],
            [sg.Button('Generate From Script')],
            [sg.Button('Regenerate with Non-Default TTS')],
            [sg.Text("Google Voice Speaking Rate (x)"), sg.Slider(range=(0.25, 4.0), default_value=1.1, resolution=.05, orientation='horizontal', key='speakingRate')],
            [sg.Text("Google Voice Pitch (cents)"), sg.Slider(range=(-20.0, 20.0), default_value=0, resolution=.1, orientation='horizontal', key='pitch')],
            [sg.Button('Quit')],
            [sg.Column([[logo_image]], justification="center")]
        ]

def GenerateGoogleTTS(title, response_text, voice, speaking_rate, pitch):
    filename = generation_utils.title_to_filename(title)
    audio_path = os.path.join("projects",filename, filename + ".aiff")
    if not os.path.exists(audio_path):
        audio_path = os.path.join("projects",filename, filename + ".mp3")
    
    if os.path.exists(audio_path):
        os.rename(audio_path, audio_path + ".old")
    generation_utils.save_audio_google_cloud(title, response_text,voice, speaking_rate, pitch)

def GenerateFakeYouTTS(title, response_text, voice):
    filename = generation_utils.title_to_filename(title)
    audio_path = os.path.join("projects",filename, filename + ".aiff")
    if not os.path.exists(audio_path):
        audio_path = os.path.join("projects",filename, filename + ".mp3")
    if os.path.exists(audio_path):
        os.rename(audio_path, audio_path + ".old")

    fakeyou.TTS(voice, response_text.replace("\n", ""), os.path.join("projects", filename, filename + ".wav"))

def GenerateUberDuckTTS(title, response_text, voice):
    filename = generation_utils.title_to_filename(title)
    audio_path = os.path.join("projects",filename, filename + ".aiff")
    if not os.path.exists(audio_path):
        audio_path = os.path.join("projects",filename, filename + ".mp3")
    if os.path.exists(audio_path):
        os.rename(audio_path, audio_path + ".old")

    uberduck.TTS(voice, response_text.replace("\n", ""), os.path.join("projects", filename, filename + ".wav"))


# Create the Window
window = sg.Window('VidGen v1.0.0', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:

    event, values = window.read()
    title = values["title"]
    prompt_type = values["promptType"]
    prompt = prompt_types[prompt_type].replace("VIDEO_TITLE", title)
    voice = values["voice"]
    speaking_rate = float(values["speakingRate"])
    pitch = float(values["pitch"])
    USE_GOOGLE_CLOUD_TTS = voice in google_voices
    USE_FAKEYOU = voice in fakeyou_voices
    USE_UBERDUCK = voice in uberduck_voices

    if event == sg.WIN_CLOSED or event == 'Quit': # if user closes window or clicks cancel
        break

    elif event == "Generate Resources":
        print("Generating script...")
        print(f"Prompt is {prompt}")
        response_text = generation_utils.generate_script(prompt)
        print("Synthesizing audio...")
        generation_utils.save_text_and_audio(title, response_text, on_mac)

        if USE_GOOGLE_CLOUD_TTS:
            GenerateGoogleTTS(title, response_text, voice, speaking_rate, pitch)

        if USE_FAKEYOU:
            GenerateFakeYouTTS(title, response_text, voice)

        if USE_UBERDUCK:
            GenerateUberDuckTTS(title, response_text, voice)

        print("Searching for images...")
        generation_utils.download_images_from_script(response_text, title, values["mediaMethod"])
        
        print("Done generating!")

    elif event == "Create Movie":
        make_movie(title, values["music"])
        print("Done making movie!")

    elif event == "Regenerate with Non-Default TTS":

        if(voice == "Default"):
            print("Cannot use Default with Non-Default TTS")
            continue

        print("Reading from script...")
        filename = generation_utils.title_to_filename(title)
        response_text = generation_utils.load_script_raw(os.path.join("projects",filename, filename + ".txt"))
        
        if USE_GOOGLE_CLOUD_TTS:
            GenerateGoogleTTS(title, response_text, voice, speaking_rate, pitch)

        if USE_FAKEYOU:
            GenerateFakeYouTTS(title, response_text, voice)

        if USE_UBERDUCK:
            GenerateUberDuckTTS(title, response_text, voice)

        print("Done generating TTS!")

    elif event == "Generate From Script":
        print("Reading from script...")
        filename = generation_utils.title_to_filename(title)

        if not os.path.exists(os.path.join("projects", filename)) or not os.path.exists(os.path.join("projects", filename, filename + ".txt")):
            print(f"No project folder and/or .txt file with name {title} exists!")
            continue

        response_text = generation_utils.generate_script(prompt)
        response_text = generation_utils.load_script_raw(os.path.join("projects",filename, filename + ".txt"))
        print("Synthesizing audio...")
        generation_utils.save_text_and_audio(title, response_text, on_mac)

        if USE_GOOGLE_CLOUD_TTS:
            GenerateGoogleTTS(title, response_text, voice, speaking_rate, pitch)

        if USE_FAKEYOU:
            GenerateFakeYouTTS(title, response_text, voice)

        if USE_UBERDUCK:
            GenerateUberDuckTTS(title, response_text, voice)

        print("Searching for images...")
        generation_utils.download_images_from_script(response_text, title, values["mediaMethod"])
        
        print("Done generating!")

window.close()