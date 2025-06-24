import re

def remove_symbols(text):
    """Supprime les symboles parasites courants (hors ponctuation utile)."""
    return re.sub(r"[^\w\s\.\,\!\?\-\(\)\'\"]+", "", text)

def merge_broken_words(lines):
    """
    Fusionne les mots coupés par un retour à la ligne ou un tiret.
    Ex: ["jou-", "eur"] -> ["joueur"]
    """
    merged = []
    skip_next = False
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
        if line.endswith('-') and i+1 < len(lines):
            merged.append(line[:-1] + lines[i+1].lstrip())
            skip_next = True
        else:
            merged.append(line)
    return merged

def filter_by_confidence(blocks, min_conf=0.6):
    """
    Enlève les blocs OCR en-dessous d'un certain score de confiance.
    blocks : liste de dicts {"text": ..., "conf": ...}
    """
    return [b for b in blocks if b.get("conf", 1) >= min_conf]

def group_blocks_by_sentence(blocks):
    """
    Regroupe les blocs OCR voisins en phrases (simple heuristique par ponctuation).
    """
    text = " ".join([b["text"] for b in blocks])
    # Split en phrases par ponctuation
    sentences = re.split(r"(?<=[\.\!\?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]

def clean_ocr_blocks(blocks, min_conf=0.6):
    """
    Pipeline complet de nettoyage OCR :
    - filtre par confiance
    - supprime symboles
    - fusionne mots coupés
    - regroupe en phrases
    """
    blocks = filter_by_confidence(blocks, min_conf)
    lines = [remove_symbols(b["text"]) for b in blocks]
    lines = merge_broken_words(lines)
    # Reconstitue des blocs pour regroupement
    cleaned_blocks = [{"text": l, "conf": 1} for l in lines if l]
    sentences = group_blocks_by_sentence(cleaned_blocks)
    return sentences

if __name__ == "__main__":
    # Exemple d'utilisation
    ocr_result = [
        {"text": "3 things I wish I knew", "conf":0.98},
        {"text": "as a young play-", "conf":0.95},
        {"text": "er...", "conf":0.97},
        {"text": "@user!##", "conf":0.30},
    ]
    cleaned = clean_ocr_blocks(ocr_result)
    print(cleaned)