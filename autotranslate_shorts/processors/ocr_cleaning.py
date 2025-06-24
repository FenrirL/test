from typing import List, Dict, Any

def clean_ocr_blocks(video_path: str) -> List[Dict[str, Any]]:
    """
    Extraction et nettoyage OCR simplifié (stub pour démo)
    """
    # TODO: Intégration pytesseract ou EasyOCR ici
    # Exemple de bloc OCR simulé
    return [
        {"frame": 0, "box": (100, 200, 300, 60), "text": "Hello world!", "confidence": 0.92},
        {"frame": 15, "box": (120, 220, 350, 65), "text": "Bienvenue à tous", "confidence": 0.95}
    ]