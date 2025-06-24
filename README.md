# 🚀 AutoTranslate Shorts

Solution professionnelle d’analyse, traduction et édition automatique de vidéos courtes.

## Fonctionnalités

- Extraction OCR, transcription audio et traduction multilingue
- Edition vidéo automatisée (overlay, audio TTS…)
- Pipeline robuste, typée, testable et extensible
- CLI unifiée et packaging Python moderne
- Sécurité et validation intégrées

## Installation

```
git clone https://github.com/FenrirL/autotranslate_shorts.git
cd autotranslate_shorts
pip install -e .
```

## Utilisation CLI

```
autotranslate video.mp4 --lang fr --output outputs/
```

## Structure du projet

```
autotranslate_shorts/
├── core/
├── processors/
├── utils/
├── cli/
└── tests/
```

## Contribution

- Fork, PR, issues bienvenus !
- Voir [tests/](tests/) pour la structure des tests unitaires

## Licence

MIT