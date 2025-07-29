from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='AHCodeCompiler',
    version='1.0.2',
    author='Akash Halder',
    description='A Python SDK for code compilation by Akash Halder. It allows developers to use this SDK and create their frontend for online code compilation',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://akashhalder.in/',
    install_requires=[
        'requests'
    ],
    license="MIT",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
