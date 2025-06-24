import requests

def translate_text(text, target_lang="en", api="google"):
    """
    Traduit le texte dans la langue cible. Fallback sur plusieurs API selon le paramètre.
    """
    # Exemple simple avec l'API LibreTranslate (open-source, gratuite)
    # Pour Google/DeepL/GPT, il faudra ajouter la clé API appropriée.
    try:
        if api == "libretranslate":
            resp = requests.post(
                "https://libretranslate.de/translate",
                data={
                    "q": text,
                    "source": "auto",
                    "target": target_lang,
                    "format": "text"
                },
                timeout=5
            )
            resp.raise_for_status()
            return resp.json().get("translatedText", text)
        # Ajouter d'autres API ici en fallback
        # elif api == "deepl":
        #     ...
    except Exception as e:
        print(f"[WARN] Traduction échouée ({api}) : {e}")
        return text  # Fallback : texte d’origine

def translate_blocks(blocks, target_langs=["en", "es"], api="libretranslate"):
    """
    Traduit chaque bloc dans plusieurs langues. 
    blocks : liste de phrases ou de dicts {"text": ...}
    Retourne une liste de dicts { "text": ..., "text_en": ..., "text_es": ... }
    """
    results = []
    for block in blocks:
        orig = block if isinstance(block, str) else block.get("text", "")
        res = {"text": orig}
        for lang in target_langs:
            res[f"text_{lang}"] = translate_text(orig, target_lang=lang, api=api)
        results.append(res)
    return results

if __name__ == "__main__":
    blocks = [
        "3 choses que j’aurais aimé savoir quand j’étais jeune joueur.",
        "Travaille les deux pieds.",
        "Joue avec des joueurs plus forts."
    ]
    trad = translate_blocks(blocks, ["en", "es"])
    for t in trad:
        print(t)