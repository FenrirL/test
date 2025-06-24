import time
from typing import List, Dict, Any
from ..processors.ocr_cleaning import clean_ocr_blocks
from ..processors.translation import translate_sentences
from ..processors.video_editing import edit_video_with_translations
from ..processors.audio_sync import generate_tts_segments, align_overlay_timing_with_tts, merge_audio_on_video
from ..utils.quality_control import generate_quality_report
from ..core.config import settings

def run_pipeline(video_path: str, target_lang: str, outdir: str = None) -> Dict[str, Any]:
    """
    Pipeline principale : OCR, traduction, édition vidéo & audio, contrôle qualité.
    """
    start_time = time.time()
    outdir = outdir or settings.output_dir
    results = {
        "success": False,
        "video_path": video_path,
        "target_language": target_lang,
        "output_directory": outdir,
        "errors": [],
        "files_generated": []
    }

    try:
        # Etape 1 : OCR & extraction textes
        ocr_boxes = clean_ocr_blocks(video_path)
        # Etape 2 : Traduction
        trad_blocks = translate_sentences([b['text'] for b in ocr_boxes], target_lang)
        # Etape 3 : Edition vidéo
        out_video = edit_video_with_translations(video_path, ocr_boxes, trad_blocks, outdir, target_lang)
        results["files_generated"].append(out_video)
        # Etape 4 : Génération audio TTS et synchronisation
        tts_segments = generate_tts_segments(trad_blocks, target_lang)
        final_video = merge_audio_on_video(out_video, tts_segments, outdir, target_lang)
        results["files_generated"].append(final_video)
        # Etape 5 : Contrôle qualité
        generate_quality_report(video_path, ocr_boxes, trad_blocks, tts_segments, outdir=outdir)
        results["success"] = True
    except Exception as e:
        results["errors"].append(str(e))
    results["processing_time"] = time.time() - start_time
    return results