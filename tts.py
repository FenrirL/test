def synthesize_tts(text, lang):
    try:
        return generer_audio_elevenlabs(text, lang)
    except Exception as e:
        print("ElevenLabs failed, fallback to pyttsx3:", e)
        return generer_audio_pyttsx3(text, lang)