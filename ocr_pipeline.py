import cv2
import pytesseract
import easyocr
from paddleocr import PaddleOCR

def ocr_all_methods(img):
    # Vérification du type
    print("Type de img:", type(img), "Shape:", getattr(img, "shape", None))

    # Tesseract (nécessite RGB)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    try:
        text_tess = pytesseract.image_to_string(img_rgb)
    except Exception as e:
        print("Tesseract failed:", e)

    # EasyOCR
    try:
        reader = easyocr.Reader(['fr', 'en'])
        result_easy = reader.readtext(img)
    except Exception as e:
        print("EasyOCR failed:", e)

    # PaddleOCR
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang='fr')
        result_paddle = ocr.ocr(img)
    except Exception as e:
        print("PaddleOCR failed:", e)