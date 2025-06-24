def generate_quality_report(video_path, ocr_boxes, trad_blocks, tts_segments, outdir="outputs"):
    """
    Génère un rapport qualité (stub)
    """
    import os, json
    os.makedirs(outdir, exist_ok=True)
    report = {
        "video": video_path,
        "ocr_blocks": len(ocr_boxes),
        "translations": len(trad_blocks),
        "tts_segments": len(tts_segments)
    }
    with open(os.path.join(outdir, "quality_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)