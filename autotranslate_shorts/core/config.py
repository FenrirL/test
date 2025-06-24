from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    elevenlabs_api_key: Optional[str] = None
    google_translate_api_key: Optional[str] = None
    default_fps: int = 25
    frame_extraction_interval: int = 30
    max_video_duration: int = 300
    temp_dir: str = "temp"
    output_dir: str = "outputs"
    max_workers: int = 4
    enable_profiling: bool = False

    class Config:
        env_file = ".env"

settings = Settings()