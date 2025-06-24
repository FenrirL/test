import json

def generate_report(script_json, output_path, tts_success=True, subtitles_generated=True, quality_score=94):
    with open(script_json, encoding="utf-8") as f:
        script = json.load(f)
    report = {
        "lang_detected": script.get("lang_detected", "und"),
        "translated_to": [k.split("_")[1] for b in script["texts"] for k in b if k.startswith("text_")],
        "duration_sec": max([b["end"] for b in script["texts"]]) if script["texts"] else 0,
        "text_blocks": len(script["texts"]),
        "tts_success": tts_success,
        "subtitles_generated": subtitles_generated,
        "quality_score": quality_score
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"✅ Rapport généré : {output_path}")