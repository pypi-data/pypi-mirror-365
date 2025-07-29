import requests
from .config import BASE_URL
from .runtimes import get_runtimes

def execute_code(language: str, version: str = None, files: list = []) -> dict:
    """
    Execute code remotely using the given language and version.

    If version is not provided, the latest supported version will be selected.

    Args:
        language (str): Programming language (e.g., 'python3', 'javascript').
        version (str, optional): Specific version (e.g., '3.10.0').
        files (list): List of dicts with file `name` and `content`.

    Returns:
        dict: JSON response including stdout, stderr, exit code, etc.

    Raises:
        requests.HTTPError: If the request fails or returns a bad status.
    """
    if not version:
        runtimes = get_runtimes()
        versions = [
            r for r in runtimes if r["language"].lower() == language.lower()
        ]
        if not versions:
            raise ValueError(f"No runtimes found for language: {language}")
        version = versions[0]["version"]

    payload = {
        "language": language,
        "version": version,
        "files": files,
    }

    try:
        res = requests.post(f"{BASE_URL}/execute", json=payload, timeout=5)
        res.raise_for_status()
        return res.json()
    except requests.HTTPError as http_err:
        # Replace "piston" with "akash-code-jobs" in error messages
        error_text = str(http_err).replace("piston", "akash-code-jobs")
        raise requests.HTTPError(error_text) from http_err
    except Exception as err:
        raise Exception(str(err).replace("piston", "akash-code-jobs")) from err
