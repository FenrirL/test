import json
import re
from deep_translator import GoogleTranslator

def clean_text_blocks(blocks):
    seen = set()
    result = []
    for block in blocks:
        txt = block.get("text", "").strip()
        if txt and txt.lower() not in seen:
            seen.add(txt.lower())
            result.append(txt)
    return result

def summarize_naive(text):
    # Version locale simplifiée : réduit à 3 phrases max
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 8]
    return ". ".join(sentences[:3]) + "." if sentences else text

def generate_summary_from_script(script_path, langs=["en", "es", "pt"]):
    with open(script_path, encoding="utf-8") as f:
        script = json.load(f)

    blocks = script.get("texts", [])
    clean_lines = clean_text_blocks(blocks)
    full_text = " ".join(clean_lines)

    # ➤ Résumé simple local (remplacer summarize_naive par une fonction GPT au besoin)
    short_summary = summarize_naive(full_text)

    script["summary"] = {"original": short_summary}

    for lang in langs:
        try:
            translated = GoogleTranslator(source='auto', target=lang).translate(short_summary)
            script["summary"][f"translated_{lang}"] = translated
        except Exception as e:
            print(f"Erreur traduction résumé vers {lang}: {e}")
            script["summary"][f"translated_{lang}"] = "[Erreur traduction]"

    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    print("✅ Résumé généré et ajouté au script.")

if __name__ == "__main__":
    import sys
    # Usage: python video_pipeline/generate_summary.py output_local/script.json en es pt
    if len(sys.argv) >= 3:
        script_path = sys.argv[1]
        langs = sys.argv[2:]
        generate_summary_from_script(script_path, langs)
    else:
        print("Usage: python video_pipeline/generate_summary.py <script_path> <lang1> <lang2> ...")