import os
import json
from config import Config  # Utilisez la classe Config centralisée
from video_pipeline.utils import setup_logger
from googletrans import Translator  # Bien que la traduction soit dans processing, on en a besoin ici pour translate_segments

logger = setup_logger("video_pipeline.subtitles")

def _format_srt_time(seconds):
    """Formate les secondes en format SRT (HH:MM:SS,MS)."""
    ms = int((seconds - int(seconds)) * 1000)
    s = int(seconds)
    h = s // 3600
    m = (s % 3600) // 60
    s = s % 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def _format_vtt_time(seconds):
    """Formate les secondes en format VTT (HH:MM:SS.MS)."""
    ms = int((seconds - int(seconds)) * 1000)
    s = int(seconds)
    h = s // 3600
    m = (s % 3600) // 60
    s = s % 60
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

def load_cache(path):
    """Charge le cache JSON depuis un fichier."""
    if path and os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(path, data):
    """Sauvegarde les données JSON dans un fichier."""
    if path:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def translate_segments(list_of_texts, dest_lang, cache_path=None):
    """Traduit une liste de textes en utilisant un cache."""
    cache = load_cache(cache_path) if cache_path else {}
    untranslated = [t for t in list_of_texts if t not in cache]
    if untranslated:
        try:
            translator = Translator()
            translations = translator.translate(untranslated, dest=dest_lang)
            if not isinstance(translations, list):
                translations = [translations]
            for orig, trans in zip(untranslated, translations):
                cache[orig] = trans.text.strip()
            if cache_path:
                save_cache(cache_path, cache)
        except Exception as e:
            logger.error(f"❌ Erreur de traduction batch pour {dest_lang}: {e}")
            raise
    return [cache.get(t, f"[ERREUR: non traduit]") for t in list_of_texts]

def export_srt(
    translated_text, 
    lang_code, 
    output_path, 
    segments=None, 
    duration=None, 
    cache_path=None
):
    """Exporte les sous-titres au format SRT."""
    max_duration = duration if duration is not None else Config.SUBTITLE.get("max_duration", 7)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            if segments and len(segments) > 0:
                original_texts = [seg['text'] for seg in segments]
                translated_texts = translate_segments(original_texts, lang_code, cache_path)
                for idx, seg in enumerate(segments, 1):
                    start = seg['start']
                    end = min(seg['end'], start + max_duration)
                    f.write(f"{idx}\n")
                    f.write(f"{_format_srt_time(start)} --> {_format_srt_time(end)}\n")
                    f.write(translated_texts[idx-1] + "\n\n")
            else:
                f.write(f"1\n00:00:00,000 --> 00:00:{max_duration:02d},000\n")
                f.write(translated_text.strip() + "\n")
        logger.info(f"✅ Sous-titres SRT exportés: {output_path}")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'export SRT: {e}")

def export_vtt(
    translated_text, 
    lang_code, 
    output_path, 
    segments=None, 
    duration=None, 
    cache_path=None
):
    """Exporte les sous-titres au format VTT."""
    max_duration = duration if duration is not None else Config.SUBTITLE.get("max_duration", 7)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n")
            if segments and len(segments) > 0:
                original_texts = [seg['text'] for seg in segments]
                translated_texts = translate_segments(original_texts, lang_code, cache_path)
                for idx, seg in enumerate(segments, 1):
                    start = _format_vtt_time(seg['start'])
                    end = _format_vtt_time(min(seg['end'], seg['start'] + max_duration))
                    f.write(f"{start} --> {end}\n")
                    f.write(translated_texts[idx-1] + "\n\n")
            else:
                f.write(f"00:00:00.000 --> 00:00:{max_duration:02d}.000\n")
                f.write(translated_text.strip() + "\n")
        logger.info(f"✅ Sous-titres VTT exportés: {output_path}")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'export VTT: {e}")