import json

def group_text_blocks(segments, merge_delta=0.5):
    grouped = []
    buffer = None
    for seg in segments:
        if buffer is None:
            buffer = seg
        elif seg['text'] == buffer['text'] and abs(seg['start'] - buffer['end']) < merge_delta:
            buffer['end'] = seg['end']  # Extend duration
        else:
            grouped.append(buffer)
            buffer = seg
    if buffer:
        grouped.append(buffer)
    return grouped

def export_script_json(blocks, lang_detected="fr", type_video="voice_ocr", output="script.json"):
    script = {
        "lang_detected": lang_detected,
        "type_video": type_video,
        "texts": blocks
    }
    with open(output, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    print(f"✅ Script exporté: {output}")