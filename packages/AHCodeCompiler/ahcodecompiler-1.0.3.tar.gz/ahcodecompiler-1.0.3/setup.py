from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='AHCodeCompiler',
    version='1.0.3',
    author='Akash Halder',
     description='A Python SDK by Akash Halder for compiling and executing code online with beautiful CLI output.',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://akashhalder.in/',
    install_requires=[
        'requests',
        'rich',
        'pyfiglet'
    ],
    license="MIT",
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
