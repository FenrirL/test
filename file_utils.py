import shutil
import os
from datetime import datetime
import hashlib

def archive_original(video_path):
    today = datetime.now().strftime("%Y-%m-%d")
    basename = os.path.splitext(os.path.basename(video_path))[0]
    archive_dir = f"./archive/{basename}_{today}/"
    os.makedirs(archive_dir, exist_ok=True)
    dest = os.path.join(archive_dir, os.path.basename(video_path))
    shutil.move(video_path, dest)
    return dest

def get_md5(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def is_duplicate(path, hash_set):
    h = get_md5(path)
    return h in hash_set