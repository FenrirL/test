import cv2
import numpy as np
import textwrap

def fit_text_to_bbox(text, bbox_width, bbox_height, font=cv2.FONT_HERSHEY_SIMPLEX, 
                     max_font_scale=2.0, min_font_scale=0.3, font_thickness=2, margin=10):
    for font_scale in np.arange(max_font_scale, min_font_scale, -0.05):
        avg_char_width = cv2.getTextSize("A", font, font_scale, font_thickness)[0][0]
        max_chars_per_line = max(1, int((bbox_width - 2*margin) // avg_char_width))
        lines = textwrap.wrap(text, width=max_chars_per_line)
        line_heights = [cv2.getTextSize(line, font, font_scale, font_thickness)[0][1] for line in lines]
        total_height = sum(line_heights) + (len(lines)-1)*5
        if total_height <= (bbox_height - 2*margin):
            return font_scale, lines
    lines = textwrap.wrap(text, width=max(1, int((bbox_width - 2*margin) // avg_char_width)))
    return min_font_scale, lines

def overlay_translated_text_autofit(
    frame, bbox, text, font=cv2.FONT_HERSHEY_SIMPLEX, font_thickness=2,
    text_color=(255,255,255), bg_color=(0,0,0), alpha=0.6, margin=10
):
    overlay = frame.copy()
    x, y, w, h = bbox
    font_scale, lines = fit_text_to_bbox(text, w, h, font, font_thickness=font_thickness, margin=margin)
    line_heights = [cv2.getTextSize(line, font, font_scale, font_thickness)[0][1] for line in lines]
    text_height = sum(line_heights) + (len(lines)-1)*5
    cv2.rectangle(overlay, (x-margin, y-margin), (x+w+margin, y+h+margin), bg_color, -1)
    frame = cv2.addWeighted(overlay, alpha, frame, 1-alpha, 0)
    current_y = y + (h - text_height)//2 + line_heights[0]
    for i, line in enumerate(lines):
        line_width = cv2.getTextSize(line, font, font_scale, font_thickness)[0][0]
        text_x = x + (w - line_width) // 2
        cv2.putText(frame, line, (text_x, current_y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)
        current_y += line_heights[i] + 5
    return frame