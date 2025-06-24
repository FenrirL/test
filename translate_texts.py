import json
from deep_translator import GoogleTranslator

def translate_texts(script_path, langs=["en", "es", "pt"]):
    with open(script_path, encoding="utf-8") as f:
        script = json.load(f)

    for block in script.get("texts", []):
        text = block.get("text", "")
        for lang in langs:
            try:
                translated = GoogleTranslator(source='auto', target=lang).translate(text)
                block[f"text_{lang}"] = translated
            except Exception as e:
                print(f"❌ Erreur traduction {text} -> {lang}: {e}")
                block[f"text_{lang}"] = "[ERROR]"

    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    print(f"✅ Traductions ajoutées à {script_path}")

if __name__ == "__main__":
    import sys
    # Usage: python video_pipeline/translate_texts.py output_local/short001_script.json en es pt
    if len(sys.argv) >= 3:
        script_path = sys.argv[1]
        langs = sys.argv[2:]
        translate_texts(script_path, langs)
    else:
        print("Usage: python video_pipeline/translate_texts.py <script_path> <lang1> <lang2> ...")