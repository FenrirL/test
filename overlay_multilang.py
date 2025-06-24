import cv2
import numpy as np
import textwrap

def wrap_text_to_box(text, max_width_px, font_scale, thickness, font=cv2.FONT_HERSHEY_SIMPLEX):
    """Découpe le texte en plusieurs lignes pour qu'il tienne dans max_width_px (largeur bbox)."""
    avg_char_width = cv2.getTextSize("A", font, font_scale, thickness)[0][0]
    max_chars_per_line = max(1, int(max_width_px // avg_char_width))
    lines = textwrap.wrap(text, width=max_chars_per_line)
    return lines

def overlay_translated_text(
    frame, bbox, translations, lang, 
    font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1.0, font_thickness=2,
    text_color=(255,255,255), bg_color=(0,0,0), alpha=0.6, margin=10
):
    """
    Ajoute le texte traduit (multi-langue) centré sur la bbox avec fond semi-transparent et retour à la ligne automatique.
    - bbox: [x, y, w, h]
    - translations: dict, par ex. {"fr": "...", "en": "...", "es": "..."}
    - lang: langue cible, ex: "fr"
    """
    overlay = frame.copy()
    x, y, w, h = bbox

    # Sélectionne le texte selon la langue (prévoir fallback)
    text = translations.get(lang) or translations.get("en") or next(iter(translations.values()))

    lines = wrap_text_to_box(text, w - 2*margin, font_scale, font_thickness)
    line_sizes = [cv2.getTextSize(line, font, font_scale, font_thickness)[0] for line in lines]
    text_height = sum([size[1] for size in line_sizes]) + (len(lines)-1)*5

    # Fond semi-transparent
    cv2.rectangle(overlay, (x-margin, y-margin), (x+w+margin, y+h+margin), bg_color, -1)
    frame = cv2.addWeighted(overlay, alpha, frame, 1-alpha, 0)

    # Centrage vertical du bloc de texte
    current_y = y + (h - text_height)//2 + line_sizes[0][1]
    for i, line in enumerate(lines):
        line_width = line_sizes[i][0]
        text_x = x + (w - line_width) // 2
        cv2.putText(frame, line, (text_x, current_y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)
        current_y += line_sizes[i][1] + 5
    return frame