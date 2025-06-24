import cv2
import pytesseract
from pytesseract import Output
import numpy as np
from moviepy.editor import VideoFileClip  # <-- IMPORT MANQUANT
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})
import re

def extract_ocr_segments(video_path, frame_interval=0.2, conf_thresh=70):
    clip = VideoFileClip(video_path)
    duration = clip.duration
    times = np.arange(0, duration, frame_interval)
    segments = []
    for t in times:
        frame = clip.get_frame(t)
        img = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        data = pytesseract.image_to_data(img, output_type=Output.DICT, config="--psm 6")
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            try:
                conf = int(float(data['conf'][i]))
            except:
                conf = 0
            if text and conf > conf_thresh:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                segments.append({
                    "start": float(t),
                    "end": float(t + frame_interval),
                    "text": text,
                    "bbox": [int(x), int(y), int(w), int(h)],
                    "confidence": conf
                })
    clip.close()
    return segments

def clean_and_group_ocr_blocks(ocr_blocks, min_confidence=85, min_length=2):
    cleaned = []
    for block in ocr_blocks:
        text = block.get("text", "").strip()
        conf = block.get("confidence", 0)
        if len(text) < min_length:
            continue
        if conf < min_confidence:
            continue
        if re.match(r"^[\W_]+$", text):
            continue
        cleaned.append(block)
    return cleaned