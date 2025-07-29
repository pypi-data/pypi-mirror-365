import requests
from .config import BASE_URL

def execute_code(language, version, files):
    payload = {
        "language": language,
        "version": version,
        "files": files
    }

    res = requests.post(f"{BASE_URL}/execute", json=payload, timeout=5)
    res.raise_for_status()
    return res.json()
