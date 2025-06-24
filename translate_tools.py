from deep_translator import GoogleTranslator
# Option: ElevenLabs or gTTS for TTS

def translate_texts(texts, src_lang, target_langs):
    """
    Ajoute text_<lang> pour chaque segment, sauf langue d'origine.
    """
    for txt_obj in texts:
        src_text = txt_obj["text"]
        for lang in target_langs:
            if lang == src_lang:
                continue
            try:
                txt_obj[f"text_{lang}"] = GoogleTranslator(source=src_lang, target=lang).translate(src_text)
            except Exception:
                txt_obj[f"text_{lang}"] = "[translation failed]"
    return texts

def tts_texts(texts, target_langs):
    """
    Génère du TTS pour chaque texte traduit (ex: ElevenLabs, gTTS, etc.)
    """
    # TODO: brancher ElevenLabs API ou gTTS ici
    pass