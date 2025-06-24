import moviepy.editor as mp
import numpy as np
import cv2
import easyocr
import whisper

def detect_audio_type(video_path, whisper_model="base"):
    """
    Analyse l'audio pour déterminer s'il y a de la parole, de la musique ou du silence.
    Retourne : 'speech', 'music', 'silence', ou 'mix'
    """
    audio_clip = mp.VideoFileClip(video_path).audio
    audio_path = "temp_audio.wav"
    audio_clip.write_audiofile(audio_path, verbose=False, logger=None)
    
    # Utilise Whisper pour détecter la parole
    model = whisper.load_model(whisper_model)
    result = model.transcribe(audio_path, language="fr")  # ou "en", à adapter
    has_speech = len(result.get("segments", [])) > 0

    # (Optionnel) Analyse simple du spectre pour détecter la musique
    # À améliorer avec une vraie détection musique/bruit/silence
    # Ici, on considère que s'il y a parole + "rythme" => mix
    # TODO : Ajouter une vraie détection musique

    if has_speech:
        return "speech"
    else:
        return "music_or_silence"

def detect_text_presence(video_path, frame_skip=10, ocr_model='en'):
    """
    Analyse quelques frames pour détecter la présence de texte à l'image.
    Retourne True si du texte est détecté.
    """
    reader = easyocr.Reader([ocr_model])
    clip = mp.VideoFileClip(video_path)
    frames_to_check = np.linspace(0, clip.duration, num=6).astype(int)
    for t in frames_to_check:
        frame = clip.get_frame(t)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        result = reader.readtext(gray)
        if any([conf > 0.5 for (_, _, conf) in result]):
            return True
    return False

def analyse_video_type(video_path):
    audio_type = detect_audio_type(video_path)
    has_text = detect_text_presence(video_path)
    if audio_type == "speech" and has_text:
        return "speech+text"
    elif audio_type == "speech":
        return "speech"
    elif has_text:
        return "text"
    else:
        return "music_or_silence"

if __name__ == "__main__":
    import sys
    video = sys.argv[1]
    print("Type de vidéo détecté :", analyse_video_type(video))