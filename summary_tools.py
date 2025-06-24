from deep_translator import GoogleTranslator

def generate_summary(texts, style="default", gpt_client=None):
    texte_complet = " ".join([t["text"] for t in texts])
    # Option : GPT pour résumé stylisé (fun, pro, poétique...)
    if gpt_client:
        prompt = f"Résume le texte suivant de façon {style} : {texte_complet}"
        # response = gpt_client.chat.completions.create(...)
        # return response.choices[0].message.content.strip()
        return "[résumé GPT ici]"
    return texte_complet[:300]

def translate_summary(summary, src_lang, target_langs):
    trad = {}
    for lang in target_langs:
        if lang == src_lang:
            continue
        try:
            trad[f"summary_{lang}"] = GoogleTranslator(source=src_lang, target=lang).translate(summary)
        except Exception:
            trad[f"summary_{lang}"] = "[translation failed]"
    return trad