import openai

# 1. Correction intelligente OCR / restructuration de texte
def correct_ocr_blocks(ocr_blocks, model="gpt-3.5-turbo"):
    """
    Prend une liste de blocs OCR [{"text":...}, ...] et retourne une liste corrigée/restructurée.
    """
    corrected_blocks = []
    for block in ocr_blocks:
        prompt = (
            "Corrige et restructure ce texte issu d'un OCR pour le rendre lisible, sans faute :\n"
            f"Texte OCR : {block['text']}\n"
            "Texte corrigé :"
        )
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
            temperature=0.2
        )
        corrected_text = response.choices[0].message.content.strip()
        block_corr = block.copy()
        block_corr["text"] = corrected_text
        corrected_blocks.append(block_corr)
    return corrected_blocks

# 2. Reformulation naturelle des traductions
def reformulate_translation(text, target_lang="en", model="gpt-3.5-turbo"):
    """
    Reformule une traduction pour la rendre naturelle et fluide.
    """
    prompt = (
        f"Peux-tu reformuler ce texte pour qu'il paraisse naturel et oral en {target_lang} ?\n"
        f"Texte à reformuler : {text}\n"
        "Texte reformulé :"
    )
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256,
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

def reformulate_translations(trad_blocs, target_lang="en", model="gpt-3.5-turbo"):
    """
    Applique la reformulation sur tous les blocs de traduction.
    """
    for bloc in trad_blocs:
        key = f"text_{target_lang}"
        if key in bloc:
            try:
                bloc[key] = reformulate_translation(bloc[key], target_lang, model=model)
            except Exception:
                continue
    return trad_blocs

# 3. Résumé automatique de la vidéo
def summarize_video(transcription, lang="fr", model="gpt-3.5-turbo"):
    """
    Prend la transcription complète en entrée, retourne un résumé synthétique.
    """
    script = " ".join([seg["text"] for seg in transcription if seg.get("text")])
    prompt = (
        f"Voici la transcription d'une vidéo. Fais-en un résumé synthétique et pertinent en {lang}.\n\n"
        f"Transcription : {script}\n\nRésumé :"
    )
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.35
    )
    return response.choices[0].message.content.strip()