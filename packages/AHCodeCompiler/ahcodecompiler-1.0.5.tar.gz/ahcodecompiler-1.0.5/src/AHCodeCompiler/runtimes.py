import requests
from .config import BASE_URL

def get_runtimes() -> list:
    """
    Fetch all available runtimes (supported languages and versions).

    Returns:
        list: A list of dictionaries containing:
              - language
              - version
              - aliases
              - runtime info

    Example:
        [
            {
                "language": "python3",
                "version": "3.10.0",
                "aliases": ["py", "python"],
                ...
            },
            ...
        ]

    Raises:
        requests.HTTPError: If the request fails.
    """
    res = requests.get(f"{BASE_URL}/runtimes", timeout=5)
    res.raise_for_status()
    return res.json()
