import requests
import hmac
import hashlib
import datetime
import time
import random

# TODO: Change this from global to using a client class
global PUBLIC_KEY
global PRIVATE_KEY
global PROJECT_ID
global USER_ID

def is_authenticated():
    return PUBLIC_KEY and PRIVATE_KEY and PROJECT_ID and USER_ID

def client(public_key, private_key, project_id, user_id):
    global PUBLIC_KEY
    global PRIVATE_KEY
    global PROJECT_ID
    global USER_ID
    PUBLIC_KEY = public_key
    PRIVATE_KEY = private_key
    PROJECT_ID = project_id
    USER_ID = user_id

# Returns a response with a list of all results of video search
def search_videos(keywords, content_type = "all", quality = "ALL", min_duration = 0, max_duration = 10000):
    # TODO: Change this check to a decorator
    if not is_authenticated():
        print("STORYBLOCKS CLIENT NOT INITIALIZED, PLEASE RUN client()")
        return

    expires = str(int(time.time()))
    HMAC = get_HMAC(expires)
    return requests.get(f"https://api.videoblocks.com/api/v2/videos/search?APIKEY={PUBLIC_KEY}&EXPIRES={expires}&HMAC={HMAC}&project_id={PROJECT_ID}&user_id={USER_ID}&keywords={keywords}&content_type={content_type}&quality={quality}&min_duration={min_duration}&max_duration={max_duration}")
    
# Returns url to random .mp4 file from keywords
def get_random_video_url(keywords, quality = "_180p"):
    res = search_videos(keywords)
    length_of_results = len(res.json()['results'])

    if(length_of_results == 0):
        print(f"NO RESULTS FOUND FOR KEY WORDS '{keywords}'. RETURNING NONE")
        return None

    index = random.randint(0, length_of_results - 1)
    return res.json()['results'][index]['preview_urls'][quality]

# Downloads random .mp4 file from keywords. Returns true if successful, false otherwise
def download_random_video(keywords, path, quality = "_180p"):
    url = get_random_video_url(keywords, quality)

    if(url == None):
        return False

    r = requests.get(url, allow_redirects=True)
    open(path, 'wb').write(r.content)
    return True

def get_HMAC(expires):
    baseUrl = "https://api.videoblocks.com"
    # Change here if you would like to not search videos
    # TODO: Make this a param instead
    resource = "/api/v2/videos/search"
    hmacBuilder = hmac.new(bytearray(PRIVATE_KEY + expires, 'utf-8'), resource.encode('utf-8'), hashlib.sha256)
    hmacHex = hmacBuilder.hexdigest()
    return hmacHex