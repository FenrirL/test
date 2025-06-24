from setuptools import setup, find_packages

setup(
    name="autotranslate-shorts",
    version="0.1.0",
    description="Traduction intelligente de vidéos courtes",
    author="FenrirL",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.5.0",
        "moviepy>=1.0.0",
        "whisper @ git+https://github.com/openai/whisper.git",
        "pytesseract>=0.3.0",
        "elevenlabs>=0.2.0",
        "deep-translator>=1.8.0",
        "tqdm>=4.64.0",
        "pydantic>=1.10.0",
        "langdetect>=1.0.9",
        "python-magic>=0.4.27",
        "pytest>=7.0.0"
    ],
    entry_points={
        'console_scripts': [
            'autotranslate=autotranslate_shorts.cli.main:main',
        ],
    },
    python_requires=">=3.8",
)