import json

def export_script_json(texts, summary, summary_trans, lang_detected, type_video, output_path):
    data = {
        "lang_detected": lang_detected,
        "type_video": type_video,
        "texts": texts,
        "summary": {"original": summary, **summary_trans}
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def export_script_txt(texts, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for txt in texts:
            f.write(f"{txt['start']:.2f} - {txt['end']:.2f}: {txt['text']}\n")

def export_summary_txt(summary, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)