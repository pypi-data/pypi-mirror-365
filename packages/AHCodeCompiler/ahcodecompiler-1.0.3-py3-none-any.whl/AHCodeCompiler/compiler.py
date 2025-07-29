from typing import List, Dict, Any
from .runtimes import get_runtimes
from .execute import execute_code
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from pyfiglet import Figlet

console = Console()

class AHCodeCompiler:
    """
    `AHCodeCompiler` is a Python SDK that allows you to:
    - Fetch available runtimes (languages and versions)
    - Execute code remotely with rich CLI-style output
    """

    def get_runtimes(self) -> List[Dict[str, Any]]:
        """
        ***Print and return all available runtimes.***
        """
        runtimes = get_runtimes()
        banner = Figlet(font="slant").renderText("Available Runtimes")
        console.print(f"[bold magenta]{banner}[/bold magenta]")

        for runtime in runtimes:
            lang = runtime.get("language", "unknown")
            version = runtime.get("version", "n/a")
            aliases = ", ".join(runtime.get("aliases", [])) or "None"
            console.print(
                Panel.fit(
                    f"[bold green]Language:[/bold green] {lang}\n"
                    f"[bold cyan]Version:[/bold cyan] {version}\n"
                    f"[bold yellow]Aliases:[/bold yellow] {aliases}",
                    box=box.ROUNDED,
                    title=f"[white]{lang}[/white]",
                    border_style="cyan"
                )
            )

        return runtimes

    def execute(self, language: str, version: str = None, files: List[Dict[str, str]] = []) -> Dict[str, Any]:
        """
        ***Execute code using given language and files.***

        Args:
            language (str): Programming language name.
            version (str, optional): Specific version. Auto-detects latest if not provided.
            files (List[Dict[str, str]]): Files with `name` and `content`.

        Prints:
            This method prints in a well-formatted CLI output.

        Returns:

            `Dict [ str, Any ]`: Execution response from server.
        """
        try:
            # Auto-detect version if not provided
            if not version:
                runtimes = get_runtimes()
                matched = [r for r in runtimes if r["language"].lower() == language.lower()]
                if not matched:
                    raise ValueError(f"No runtimes found for language: {language}")
                version = matched[0]["version"]

            response = execute_code(language, version, files)
            stdout = response.get("run", {}).get("stdout", "")
            stderr = response.get("run", {}).get("stderr", "")
            has_errors = bool(stderr and stderr.strip())

            banner = Figlet(font="slant").renderText("AH Code Compiler SDK")
            console.print(f"[bold green]{banner}[/bold green]" if not has_errors else f"[bold red]{banner}[/bold red]")

            if has_errors:
                console.print("[bold red]❌ Code Executed with Errors[/bold red]")
            else:
                console.print("[bold green]✅ Code Executed Successfully![/bold green]")

            if stdout:
                console.print(Panel.fit(stdout.strip(), title="📤 Output", style="green", box=box.ROUNDED))

            if has_errors:
                lines = stderr.strip().split("\n")
                styled = []
                for line in lines:
                    line = line.replace("/piston/", "/akash-code-jobs/")
                    if "error" in line.lower() or "syntaxerror" in line.lower():
                        styled.append(f"[bold red]{line}[/bold red]")
                    elif "warning" in line.lower():
                        styled.append(f"[bold yellow]{line}[/bold yellow]")
                    else:
                        styled.append(f"[grey50]{line}[/grey50]")

                console.print(
                    Panel.fit(
                        "\n".join(styled),
                        title="⚠️ Warnings / Stderr",
                        style="yellow",
                        box=box.ROUNDED
                    )
                )

            return response

        except Exception as e:
            banner = Figlet(font="slant").renderText("AH Code Compiler SDK")
            error_text = str(e).replace("piston", "akash-code-jobs")
            console.print(f"[bold red]{banner}[/bold red]")
            console.print("[bold red]❌ Code Execution Failed[/bold red]")
            console.print(Panel.fit(error_text, title="⛔ Error", style="red", box=box.HEAVY))
            return {"success": False, "error": error_text}

    def help(self):
        """
        ***Print CLI-style SDK usage help.***
        """
        figlet = Figlet(font="slant")
        console.print(f"[bold cyan]{figlet.renderText('AH Code Compiler SDK')}[/bold cyan]")

        help_text = Text()
        help_text.append("🧠 Description:\n", style="bold underline")
        help_text.append("  A Python SDK to compile & run code remotely with CLI-style output.\n\n")

        help_text.append("🛠️ Methods:\n", style="bold underline")
        help_text.append("  get_runtimes() -> List[Dict]:\n", style="bold blue")
        help_text.append("    Print and return all supported languages and versions.\n\n")

        help_text.append("  execute(language, version=None, files=[]) -> Dict:\n", style="bold blue")
        help_text.append("    Execute code with auto-detected version if not specified.\n\n")

        help_text.append("🚀 Example:\n", style="bold underline")
        help_text.append(
            """
                from AHCodeCompiler import AHCodeCompiler

                compiler = AHCodeCompiler()

                # Show available languages
                compiler.get_runtimes()

                # Run code
                compiler.execute(
                    language="python3",
                    files=[{"name": "main.py", "content": "print('Hello from CLI!')"}]
                )

                # Show CLI Help
                compiler.help()
                        \n""",
                        style="dim"
            )

        help_text.append("📦 Docs: https://pypi.org/project/AHCodeCompiler/\n", style="bold magenta")
        help_text.append("👨‍💻 Developer/Author: Akash Halder\n", style="bold yellow")

        console.print(Panel(help_text, title="CLI Help", border_style="cyan", box=box.DOUBLE_EDGE))
