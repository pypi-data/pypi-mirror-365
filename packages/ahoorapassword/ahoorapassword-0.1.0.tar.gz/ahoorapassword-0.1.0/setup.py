from setuptools import setup, find_packages

setup(
    name="ahoorapassword",
    version="0.1.0",
    author="AH00RA0",
    description="A simple password generator that copies output to clipboard automatically.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["colorama", "pyperclip"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)