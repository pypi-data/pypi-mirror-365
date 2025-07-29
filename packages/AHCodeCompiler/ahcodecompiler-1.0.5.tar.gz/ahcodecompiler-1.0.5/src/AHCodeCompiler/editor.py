from AHCodeCompiler import AHCodeCompiler
from pyfiglet import Figlet
import io
from contextlib import redirect_stdout


class CLICodeEditor:
    """
    A simple command-line interface (CLI) code editor and runner using the AHCodeCompiler.
    """

    def __init__(self):
        """
        Initializes the CLICodeEditor with a compiler instance and sets up
        a mapping between supported languages and their runtime configurations.
        """
        self.compiler = AHCodeCompiler()
        self.language_to_config_map = {}

    def _load_runtimes(self, verbose=False):
        """
        Loads supported runtimes from the AHCodeCompiler and populates the
        `language_to_config_map` with language-specific configurations.

        Args:
            verbose (bool): Whether to print runtime information.

        Returns:
            bool: True if runtimes were loaded successfully, False otherwise.
        """
        if verbose:
            print("\n📡 Fetching supported runtimes...\n")
            runtimes = self.compiler.get_runtimes()
        else:
            with redirect_stdout(io.StringIO()):
                runtimes = self.compiler.get_runtimes()

        if not runtimes:
            if verbose:
                print("❌ No runtimes found.")
            return False

        self.language_to_config_map.clear()

        for rt in runtimes:
            lang = rt.get("language", "").lower()
            runtime = rt.get("runtime") or lang
            filename = (
                rt.get("example", {}).get("files", [{}])[0].get("name")
                or f"main.{lang[:2]}"
            )

            if not lang or not runtime:
                continue

            self.language_to_config_map[lang] = {
                "runtime": runtime,
                "language": lang,
                "filename": filename
            }

        return True

    def _get_user_code_input(self, language):
        """
        Prompts the user to enter source code for the given language.

        Args:
            language (str): The programming language being used.

        Returns:
            str: Full source code as a string.
        """
        print(f"\n → Enter your {language} code below.")
        print("🔚 Type 'END_CODE' on a new line to finish.\n")
        code_lines = []
        while True:
            line = input()
            if line.strip().upper() == "END_CODE":
                break
            code_lines.append(line)
        return "\n".join(code_lines)

    def _execute(self, language, runtime, filename, code):
        """
        Executes the given code using AHCodeCompiler.

        Args:
            language (str): Language name.
            runtime (str): Runtime string.
            filename (str): Name of the file.
            code (str): Source code.
        """
        print(f"\n🚀 Executing your {language} code with runtime: {runtime}...\n")
        self.compiler.execute(
            language=language,
            files=[{"name": filename, "content": code}]
        )

    def run_code_editor(self):
        """
        Runs the interactive CLI code editor.
        """
        if not self._load_runtimes(verbose=False):
            print("⚠️ Could not load runtimes.")
            return

        while True:
            lang_input = input("\nEnter language (or 'exit' to go back): ").strip().lower()
            if lang_input == "exit":
                print("👋 Returning to main menu.")
                break

            if lang_input not in self.language_to_config_map:
                print("⚠️ Unsupported language. Please try again.")
                continue

            config = self.language_to_config_map[lang_input]
            user_code = self._get_user_code_input(lang_input)

            if not user_code.strip():
                print("⚠️ No code entered.")
                continue

            self._execute(
                language=config["language"],
                runtime=config["runtime"],
                filename=config["filename"],
                code=user_code
            )

    def start(self):
        """
        Starts the CLI application and handles the main menu.
        """
        print(Figlet(font='doom',width=200).renderText('AH Code CLI Editor & Runner'))

        while True:
            print("\n📋 Menu:")
            print("1. Get Available Runtimes and Languages")
            print("2. Open CLI Code Editor and Runner")
            print("3. Exit")

            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self._load_runtimes(verbose=True)
            elif choice == "2":
                self.run_code_editor()
            elif choice == "3":
                print("👋 Exiting. Thanks for using our Editor!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")

# This is the entrypoint the user will call: editor.start()
Editor = CLICodeEditor()