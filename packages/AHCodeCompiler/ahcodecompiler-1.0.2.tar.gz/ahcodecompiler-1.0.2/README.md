<img src="https://ik.imagekit.io/AkashPortfolioAssets/code-compiler-og-img.png" height="270" width="1500" alt="ah_code_compiler_banner_img"> 

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.x-green.svg)](https://pypi.org/project/ah-code-compiler-sdk/)
[![Website](https://img.shields.io/badge/🌐%20Visit%20my%20portfolio-akashhalder.in-blue)](https://akashhalder.in/portfolio)

A lightweight **Python SDK** to compile and execute code using a powerful code-execution API. Perfect for building online code editors, testing environments, and educational platforms.

> ✅ A Python port of the original [TypeScript SDK](https://www.npmjs.com/package/ah_code_compiler_sdk)

🎯 Try the live demo here: https://www.akashhalder.in/code-compiler

---

## ✨ Features

- Fetch supported runtimes with versions
- Execute code in 50+ programming languages
- Built-in error/output handling
- Easy to plug into any Python backend or CLI tool

---

## 📦 Installation

```bash
pip install ah-code-compiler-sdk
````


## 🚀 Usage (Python)

```python
import AHCodeCompiler.compiler as compiler

# Get all run-time Environment
runtimes = compiler.get_runtimes()
print("Available Runtimes: \n", runtimes)

# Execute Code of the Supported Language
result = compiler.execute_code(
    language="javascript",
    version="18.15.0",
    files=[
        {
            "name": "main.js",
            "content": "console.log('Hello from JavaScript!');"
        }
    ]
)

# Extract output and error
stdout = result.get('run', {}).get('stdout')
stderr = result.get('run', {}).get('stderr')

# Conditional rendering
if stdout:
    print("✅ Output:")
    print(stdout.strip())
elif stderr:
    print("❌ Error:")
    print(stderr.strip())
else:
    print("⚠️ No output or error received.")


```

***Or,***

```python
from AHCodeCompiler import AHCodeCompiler

compiler = AHCodeCompiler()

# Get all run-time Environment
runtimes = compiler.get_runtimes() 
print("Available runtimes: \n", runtimes)

# Execute Code of the Supported Language
result = compiler.execute(
    language="javascript",
    version="18.15.0",
    files=[
        {
            "name": "main.js",
            "content": "console.log('Hello from JavaScript!');"
        }
    ]
)

# Extract output and error
stdout = result.get('run', {}).get('stdout')
stderr = result.get('run', {}).get('stderr')

# Conditional rendering
if stdout:
    print("✅ Output:")
    print(stdout.strip())
elif stderr:
    print("❌ Error:")
    print(stderr.strip())
else:
    print("⚠️ No output or error received.")

```

---

## 📚 API Reference

### `class AHCodeCompiler`

Main SDK wrapper for all functionality.

#### `get_runtimes() -> list[dict]`

Fetch all supported runtimes.

Returns:

```python
[
  {
    "language": "python3",
    "version": "3.10.0",
    "aliases": ["py", "py3"],
    "runtime": "python"
  },
  ...
]
```

#### `execute_code(language: str, version: str, files: list[dict]) -> dict`

Execute code for the given language and version.

Example:

```python
compiler.execute_code(
    language="python3",
    version="3.10.0",
    files=[
        {"name": "main.py", "content": "print('Hello World')"}
    ]
)
```

## 🌍 Supported Languages

Some of the popular languages supported:

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
* ...and more

> Use `get_runtimes()` to fetch the latest list.


## 📄 License

MIT License © [Akash Halder](https://www.akashhalder.in/portfolio)

