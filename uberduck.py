from statistics import mode
from dotenv import load_dotenv
import requests
import uuid
import time
import os
from requests.auth import HTTPBasicAuth

from storyblocks import PRIVATE_KEY

load_dotenv()

PUBLIC_KEY = os.getenv('UBERDUCK_PUBLIC')
SECRET_KEY = os.getenv('UBERDUCK_SECRET')

def valid():
    return PUBLIC_KEY and PRIVATE_KEY

def get_models_json():
    url = "https://api.uberduck.ai/voices?mode=tts-basic"
    res = requests.get(url)
    return res.json()

def get_all_model_names():
    models = get_models_json()
    names = []
    for model in models:
        names.append(model['display_name'])
    return names

def get_model_by_name(name):
    models = get_models_json()
    for model in models:
        if model['display_name'] == name:
            return model
    return None

def get_model_id_by_name(name):
    models = get_models_json()
    for model in models:
        if model['display_name'] == name:
            return model['name']
    return None

def make_TTS_request(name, text):
    url = "https://api.uberduck.ai/speak"

    payload = {
        "voice": name,
        "pace": 1,
        "speech": text
    }
    headers = {
        "Accept": "application/json",
        "uberduck-id": "anonymous",
        "Content-Type": "application/json",
    }

    x = requests.post(url, json=payload, headers=headers, auth=HTTPBasicAuth(PUBLIC_KEY, SECRET_KEY))
    res = x.json()

    if 'detail' in res:
        print(res)
    
    return res['uuid']

def download_wav(url, path):
    r = requests.get(url, allow_redirects=True)
    open(path, 'wb').write(r.content)

def wait_until_TTS_done(uuid):
    completed = False
    while not completed:
        print("WAITING FOR JOB TO FINISH ON UBERDUCK")
        url = f"https://api.uberduck.ai/speak-status?uuid={uuid}"
        headers = {"Accept": "application/json"}
        x = requests.get(url, headers=headers)
        res = x.json()

        if res["finished_at"] is not None:
            return res["path"]
        
        if res["failed_at"] is not None:
            print(f"TTS request failed ({res['failed_at']})")
            return None

        time.sleep(1)

def TTS(model_name, text, output_path):
    uuid = make_TTS_request(get_model_id_by_name(model_name), text)
    if not uuid:
        return None

    url = wait_until_TTS_done(uuid)

    if not url:
        print("URL recieved not valid")
        return None
    
    print("JOB DONE, DOWNLOADING WAV")
    download_wav(url, output_path)