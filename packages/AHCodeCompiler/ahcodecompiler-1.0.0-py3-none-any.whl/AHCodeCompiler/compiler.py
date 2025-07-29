from typing import List, Dict, Any
from .runtimes import get_runtimes
from .execute import execute_code

class AHCodeCompiler:
    """
    AHCodeCompiler is a Python SDK that allows you to:
    - Fetch available runtimes (languages and versions)
    - Execute code snippets remotely
    """

    def get_runtimes(self) -> List[Dict[str, Any]]:
        """
        Get all available runtimes (languages & versions) supported by the SDK.

        Returns:
            List[Dict[str, Any]]: A list of available language runtimes.
        """
        return get_runtimes()

    def execute(self, language: str, version: str, files: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Execute code using the given language, version, and files.

        Args:
            language (str): The programming language (e.g., 'python3').
            version (str): The language version (e.g., '3.10.0').
            files (List[Dict[str, str]]): A list of files with `name` and `content`.

        Returns:
            Dict[str, Any]: The execution result, including stdout, stderr, etc.
        """
        return execute_code(language, version, files)

