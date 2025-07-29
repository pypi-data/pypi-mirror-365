<img src="https://ik.imagekit.io/AkashPortfolioAssets/code-compiler-og-img.png" height="270" width="1500" alt="ah_code_compiler_banner_img"> 

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.x-green.svg)](https://pypi.org/project/ah-code-compiler-sdk/)
[![Website](https://img.shields.io/badge/🌐%20Visit%20my%20portfolio-akashhalder.in-blue)](https://akashhalder.in/portfolio)

A lightweight **Python SDK** to compile and execute code using a powerful code-execution API. Perfect for building online code editors, testing environments, and educational platforms.

> ***A Python port of the original [TypeScript SDK](https://www.npmjs.com/package/ah_code_compiler_sdk)***

🎯 Try the live demo here: https://www.akashhalder.in/code-compiler

---

## ✨ Features

- Fetch supported runtimes with versions
- Execute code in 50+ programming languages
- Beautiful CLI output
- Intelligent error and warning formatting
- Easy-to-use abstraction via `AHCodeCompiler` class
- Built-in `compiler.help()` method for usage reference
- **Bonus**: Comes with a ready-to-use CLI code editor (`editor.start()`)

---

## 📦 Installation

```bash
pip install ahcodecompiler

# In Jupyter notebook / lab or Google Collab
!pip install ahcodecompiler
```


## 🚀 Usage (Python)

```python
from AHCodeCompiler import AHCodeCompiler

compiler = AHCodeCompiler()

# Get all Runtimes
compiler.get_runtimes()

# Execute Code via this method
compiler.execute(
    language="javascript",
    files=[
        {
            "name": "main.js", 
            "content": "console.log('🔥 Hello!')"
        }
    ]
)

# Get usage help
compiler.help()

```


## 🖥️ Interactive CLI Code Editor

This SDK ships with an ready to use **CLI-based code editor and runner** which internally uses the same `AHCodeCompiler` class.

### Usage:

```python
from AHCodeCompiler import Editor

Editor.start()
```

### What It Does??
* Prompts user to select a language
* Loads available runtimes from the API
* Accepts multiline code input
* Automatically detects appropriate filename
* Displays output and error in styled CLI format
---

## 📚 API Reference

### `class AHCodeCompiler`

Main SDK wrapper for all functionality.

#### `get_runtimes() -> List[Dict]`

Fetch all supported runtimes (languages + versions).

#### `execute(language: str, version: str = None, files: List[Dict[str, str]]) -> Dict`

Execute code using the given language, version, and files.

**Auto-detects version if not provided.**

```python
compiler.execute(
    language="python",
    files=[{"name": "main.py", "content": "print('Hello World')"}]
)
```

#### `help()`
Print a beautiful CLI-style usage guide right in your terminal.



## 🧪 Advanced CLI Output
* ✅ Success Panels (Green)
* ⚠️ Stderr Panels (Yellow/Red with colorized error/warning lines)
* ⛔ Error Panels (if execution fails)



## 🌍 Supported Languages

Some popular languages include:

* Python (`python3`)
* JavaScript (`node`)
* C++
* Java
* Go
* Rust
* TypeScript
* C#
* Ruby
* PHP
* ...and many more!

> Use `compiler.get_runtimes()` to fetch the full, up-to-date list.

---

## 🧠 Why Use This?

- Makes building compilers, online editors, judge systems easy
- Just plug & play, no complex setup
- Clean abstraction for both beginners & advanced devs
- Same SDK is available in [TypeScript](https://npmjs.com/package/ah_code_compiler_sdk)

---

## 📄 License

MIT License © [Akash Halder](https://www.akashhalder.in/portfolio)
