import json
import os
from datetime import datetime

def compute_quality_score(ocr_boxes, trad_blocs, tts_segments, errors):
    """
    Renvoie un score global de qualité pour la vidéo entre 0 et 100,
    basé sur la confiance OCR, la complétude de la traduction, la réussite TTS, et l'absence d'erreurs.
    """
    details = {}

    # OCR quality (moyenne des "conf")
    if ocr_boxes:
        mean_ocr_conf = sum(b.get("conf", 1.0) for b in ocr_boxes) / len(ocr_boxes)
        ocr_score = int(mean_ocr_conf * 100)
    else:
        ocr_score = 0
    details["ocr_score"] = ocr_score

    # Traduction: % de blocs traduits sans fallback
    if trad_blocs:
        n_ok = sum(1 for b in trad_blocs if b.get("text_en", "").strip() and b.get("text_en") != b.get("text", ""))
        trad_score = int(100.0 * n_ok / len(trad_blocs))
    else:
        trad_score = 0
    details["translation_score"] = trad_score

    # TTS: % de segments audio générés sans erreur
    if tts_segments:
        n_audio = sum(1 for seg in tts_segments if seg.get("audio") and seg.get("duration",0)>0)
        tts_score = int(100.0 * n_audio / len(tts_segments))
    else:
        tts_score = 0
    details["tts_score"] = tts_score

    # Export: simple, 100 si pas d'erreurs fatales
    export_score = 100 if not errors else 0
    details["export_score"] = export_score

    # Pondération : tu peux pondérer selon l'importance de chaque étape
    global_score = int((ocr_score + trad_score + tts_score + export_score) / 4)
    details["global_score"] = global_score

    return global_score, details

def generate_quality_report(
    video_path,
    ocr_boxes,
    trad_blocs,
    tts_segments,
    errors=None,
    outdir="outputs"
):
    """
    Génère un rapport qualité .json avec logs de chaque phase et score global.
    """
    errors = errors or []
    os.makedirs(outdir, exist_ok=True)
    global_score, detail_scores = compute_quality_score(ocr_boxes, trad_blocs, tts_segments, errors)

    report = {
        "video": os.path.basename(video_path),
        "datetime": datetime.now().isoformat(),
        "quality_scores": detail_scores,
        "errors": errors,
        "ocr_blocks": len(ocr_boxes) if ocr_boxes else 0,
        "translated_blocks": len(trad_blocs) if trad_blocs else 0,
        "tts_segments": len(tts_segments) if tts_segments else 0,
    }

    report_path = os.path.join(outdir, "quality_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Rapport qualité exporté : {report_path}")
    return report_path