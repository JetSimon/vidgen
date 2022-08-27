import requests
from random import choice

global PEXELS_API_KEY

def init(api_key):
    global PEXELS_API_KEY
    PEXELS_API_KEY = api_key

def download_random_video(params, path):
    x = requests.get(f"https://api.pexels.com/videos/search?query={params}&per_page=20&orientation=landscape", headers = {"Authorization":PEXELS_API_KEY})
    results = x.json()

    if ('error' in results):
        print(f"Request to Pexels had error: {results['error']}, returning False")
        return False

    if len(results["videos"]) == 0:
        return False

    url = choice(choice(results["videos"])["video_files"])["link"]

    if(url == None):
        return False

    r = requests.get(url, allow_redirects=True)
    open(path, 'wb').write(r.content)

    return True
