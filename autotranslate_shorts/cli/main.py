import argparse
from ..core.pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="AutoTranslate Shorts - Traduction intelligente de vidéos courtes")
    parser.add_argument("video_path", help="Chemin vers la vidéo à traiter")
    parser.add_argument("--lang", default="fr", help="Langue cible")
    parser.add_argument("--output", default=None, help="Dossier de sortie")
    args = parser.parse_args()
    result = run_pipeline(args.video_path, args.lang, args.output)
    print("\n==== Résultats ====")
    print(result)