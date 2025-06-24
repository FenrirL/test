from typing import List

def generate_tts_segments(trad_blocks: List[str], lang: str) -> List[str]:
    """
    Génère des segments audio TTS (stub)
    """
    # TODO: Intégrer ElevenLabs ou un moteur TTS
    return [f"TTS({s})" for s in trad_blocks]

def align_overlay_timing_with_tts(ocr_boxes, tts_segments, fps=25):
    """
    Stub d'alignement overlay/TTS
    """
    return {}

def merge_audio_on_video(video_path, tts_segments, outdir, lang) -> str:
    """
    Fusionne l'audio TTS à la vidéo (stub)
    """
    out_video = os.path.join(outdir, f"video_final_{lang}.mp4")
    with open(out_video, "w") as f:
        f.write("Fake final video content")
    return out_video