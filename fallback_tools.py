import logging

# ---------- MULTI-OCR ----------
def ocr_with_fallback(image, ocr_methods=None):
    """
    Essaie chaque méthode OCR dans l'ordre jusqu'à succès.
    ocr_methods: liste de fonctions (image) -> [{"text":..., "conf":..., ...}, ...]
    Retourne la première sortie non vide, ou [] si toutes échouent.
    """
    if ocr_methods is None:
        ocr_methods = [ocr_tesseract, ocr_easyocr, ocr_paddle]
    for method in ocr_methods:
        try:
            result = method(image)
            if result and any(b['text'].strip() for b in result):
                logging.info(f"OCR réussi avec {method.__name__}")
                return result
        except Exception as e:
            logging.warning(f"OCR {method.__name__} échoué : {e}")
    logging.error("Toutes les méthodes OCR ont échoué.")
    return []

def ocr_tesseract(image):
    import pytesseract
    from PIL import Image
    if not isinstance(image, Image.Image):
        image = Image.fromarray(image)
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang="fra+eng")
    blocks = []
    for i in range(len(data["text"])):
        if int(data["conf"][i]) > 0 and data["text"][i].strip():
            blocks.append({
                "text": data["text"][i],
                "conf": float(data["conf"][i]) / 100,
                "box": (data["left"][i], data["top"][i], data["width"][i], data["height"][i])
            })
    return blocks

def ocr_easyocr(image):
    import easyocr
    import numpy as np
    reader = easyocr.Reader(['fr', 'en'], gpu=False)
    result = reader.readtext(np.array(image))
    blocks = []
    for (bbox, text, conf) in result:
        x1, y1 = bbox[0]
        x2, y2 = bbox[2]
        blocks.append({
            "text": text,
            "conf": conf,
            "box": (int(x1), int(y1), int(x2-x1), int(y2-y1))
        })
    return blocks

def ocr_paddle(image):
    from paddleocr import PaddleOCR
    import numpy as np
    ocr = PaddleOCR(use_angle_cls=True, lang="fr")
    result = ocr.ocr(np.array(image), cls=True)
    blocks = []
    for line in result[0]:
        txt, conf = line[1][0], line[1][1]
        x1, y1 = line[0][0][0]
        x2, y2 = line[0][2][0]
        blocks.append({
            "text": txt,
            "conf": conf,
            "box": (int(x1), int(y1), int(x2-x1), int(y2-y1))
        })
    return blocks

# ---------- MULTI-API TRADUCTION ----------
def translate_with_fallback(texts, target_lang="en", engines=None):
    """
    Essaie chaque moteur de traduction jusqu'au succès.
    texts: list of str
    engines: liste de fonctions (texts, target_lang) -> [str]
    Retourne la première traduction non vide.
    """
    if engines is None:
        engines = [translate_google, translate_deepl, translate_gpt]
    for engine in engines:
        try:
            trad = engine(texts, target_lang)
            if trad and all(t.strip() for t in trad):
                logging.info(f"Traduction réussie avec {engine.__name__}")
                return trad
        except Exception as e:
            logging.warning(f"Traduction {engine.__name__} échouée : {e}")
    logging.error("Toutes les API de traduction ont échoué.")
    return [""] * len(texts)

def translate_google(texts, target_lang):
    from googletrans import Translator
    translator = Translator()
    return [translator.translate(t, dest=target_lang).text for t in texts]

def translate_deepl(texts, target_lang):
    import deepl
    auth_key = "YOUR_DEEPL_API_KEY"  # À configurer
    translator = deepl.Translator(auth_key)
    return [translator.translate_text(t, target_lang=target_lang.upper()).text for t in texts]

def translate_gpt(texts, target_lang):
    import openai
    openai.api_key = "YOUR_OPENAI_API_KEY"
    results = []
    for t in texts:
        prompt = f"Traduire en {target_lang} : {t}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
            temperature=0.2
        )
        trad = response.choices[0].message.content.strip()
        results.append(trad)
    return results