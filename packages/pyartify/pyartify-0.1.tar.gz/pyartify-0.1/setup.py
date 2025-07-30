
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyartify",
    version="0.1",
    author="Shreeya Singh",

    description="Convert images to pixel art using retro palettes like NES, GameBoy, Minecraft, and PICO-8.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shreeya2424/pyart",
    project_urls={
    "Source": "https://github.com/shreeya2424/pyart",
    "Bug Tracker": "https://github.com/shreeya2424/pyart/issues",
    },
    packages=find_packages(),
    install_requires=["Pillow", "numpy"],
    python_requires=">=3.7",
)
