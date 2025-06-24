import json
from datetime import datetime
import os

def log_video_status(filename, status, source, langs, errors, duration):
    os.makedirs("./logs", exist_ok=True)
    log_entry = {
        "filename": filename,
        "status": status,
        "source": source,
        "langs": langs,
        "errors": errors,
        "duration": duration,
        "processed_at": datetime.now().isoformat(timespec='seconds')
    }
    log_path = f"./logs/{filename}.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, indent=2)