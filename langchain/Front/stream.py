import requests
import json
from streamlit_lottie import st_lottie

def load_lottiefile(filepath: str):
        with open(filepath, "r") as f:
            return json.load(f)


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()