import easyocr

def get_ocr_boxes(video_path, frame_step=15, lang='fr'):
    """
    Renvoie une liste de dicts {frame, bbox, text, conf}
    """
    import cv2
    reader = easyocr.Reader([lang])
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    res = []
    frame_num = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_num % frame_step == 0:
            out = reader.readtext(frame)
            for bbox, txt, conf in out:
                res.append({
                    "frame": frame_num,
                    "bbox": bbox,  # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
                    "text": txt,
                    "confidence": conf
                })
        frame_num += 1
    cap.release()
    return res