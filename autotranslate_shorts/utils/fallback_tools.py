def ocr_with_fallback(frame):
    """
    Fallback OCR method (à remplacer)
    """
    return [{"box": (0,0,100,50), "text": "Fallback OCR", "conf": 0.8}]