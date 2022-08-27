from statistics import mode
import requests
import uuid
import time

def get_models_json():
    x = requests.get("https://api.fakeyou.com/tts/list")
    res = x.json()
    if 'success' not in res:
        print("failed to fetch models")
        return None
    return res

def get_all_model_names():
    res = get_models_json()
    models = res['models']
    names = []
    for model in models:
        names.append(model['title'])
    return names

def get_model_by_name(name):
    res = get_models_json()
    models = res['models']
    for model in models:
        if model['title'] == name:
            return model
    return None

def make_TTS_request(name, text):
    model = get_model_by_name(name)
    uuid_code = str(uuid.uuid4())
    model_token = model['model_token']
    data = {'uuid_idempotency_token':uuid_code, 'tts_model_token':model_token, 'inference_text':text}
    x = requests.post('https://api.fakeyou.com/tts/inference', json = data)
    res = x.json()
    if 'success' in res:
        return res['inference_job_token']
    else:
        print("TTS Request not a success")
        return None

def download_wav(partial_url, path):
    r = requests.get("https://storage.googleapis.com/vocodes-public" + partial_url, allow_redirects=True)
    open(path, 'wb').write(r.content)

def wait_until_TTS_done(job_token):
    completed = False
    while not completed:
        print("WAITING FOR JOB TO FINISH ON FAKEYOU")
        x = requests.get(f"https://api.fakeyou.com/tts/job/{job_token}")
        res = x.json()
        state = res['state']['status']

        if state == "complete_success":
            return res['state']["maybe_public_bucket_wav_audio_path"]
        
        if state == "complete_failure" or state == "attempt_failed" or state == "dead":
            print(f"TTS request failed with state {state}")
            return None

        if state == "pending" or state == "started":
            print(f"Job is {state}...")

        time.sleep(1)

def TTS(model_name, text, output_path):
    job_token = make_TTS_request(model_name, text)
    if not job_token:
        return None
    partial_url = wait_until_TTS_done(job_token)

    if not partial_url:
        print("Partial URL recieved not valid")
        return None
    
    download_wav(partial_url, output_path)