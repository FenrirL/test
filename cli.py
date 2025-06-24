import argparse
from video_pipeline.auto_edit import remove_silences
from video_pipeline.music_tools import add_music
from video_pipeline.text_removal import remove_text_with_inpainting
from video_pipeline.text_overlay import overlay_translated_text
from video_pipeline.thumbnail import generate_thumbnail

def main():
    parser = argparse.ArgumentParser(description="Pipeline de montage vidéo automatisé multilingue")
    parser.add_argument("--input", required=True, help="Vidéo source")
    parser.add_argument("--music", required=True, help="Musique de fond")
    parser.add_argument("--lang", required=True, help="Langue cible pour texte")
    parser.add_argument("--output", required=True, help="Vidéo finale")
    args = parser.parse_args()

    # 1. Suppression silences
    silentless = "tmp_no_silence.mp4"
    remove_silences(args.input, silentless)

    # 2. Ajout musique
    with_music = "tmp_music.mp4"
    add_music(silentless, args.music, with_music)

    # 3. (Suppression texte + overlay texte traduit = pipeline OCR à intégrer ici)

    # 4. Générer thumbnail
    generate_thumbnail(with_music, args.output.replace(".mp4", ".jpg"))

    # 5. Finalisation
    print("Vidéo finale prête :", args.output)

if __name__ == "__main__":
    main()