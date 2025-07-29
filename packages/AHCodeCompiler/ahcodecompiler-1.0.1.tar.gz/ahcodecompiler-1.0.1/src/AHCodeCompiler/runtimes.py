import requests
from .config import BASE_URL

def get_runtimes():
    res = requests.get(f"{BASE_URL}/runtimes",timeout=5)
    res.raise_for_status()
    return res.json()