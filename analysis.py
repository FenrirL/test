import librosa
import whisper

def detect_audio_language(audio_path):
    model = whisper.load_model("small")
    result = model.transcribe(audio_path, verbose=False)
    return result.get("language", "und")

def segment_audio(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    # Simple segmentation (à améliorer selon besoin)
    rms = librosa.feature.rms(y=y)[0]
    voiced = rms > (rms.mean() * 0.7)
    segments = []
    start = None
    for i, v in enumerate(voiced):
        t = i * 512 / sr
        if v and start is None:
            start = t
        elif not v and start is not None:
            segments.append({"start": start, "end": t, "type": "speech"})
            start = None
    if start is not None:
        segments.append({"start": start, "end": len(y)/sr, "type": "speech"})
    return segments