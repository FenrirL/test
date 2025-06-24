import moviepy.editor as mp
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import requests

LANG_COLORS = {
    "en": (255, 255, 255),     # blanc
    "es": (255, 220, 120),     # jaune pâle
    "fr": (120, 200, 255),     # bleu clair
    # Ajoute d'autres couleurs par langue ici
}

def inpaint_with_lama(frame, mask):
    _, frame_png = cv2.imencode('.png', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    _, mask_png = cv2.imencode('.png', mask)
    files = {
        'image': ('frame.png', frame_png.tobytes(), 'image/png'),
        'mask': ('mask.png', mask_png.tobytes(), 'image/png')
    }
    response = requests.post("http://localhost:5000/inpaint", files=files, timeout=30)
    if response.ok:
        nparr = np.frombuffer(response.content, np.uint8)
        result = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
    else:
        print("[WARN] Inpainting IA échoué, fallback OpenCV.")
        return cv2.inpaint(frame, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

def overlay_text(
    frame,
    text,
    box,
    font_path='arial.ttf',
    font_size=36,
    color=(255,255,255),
    opacity=1.0,
    animation=None,
    progress=1.0
):
    """
    Ajoute le texte traduit sur la frame.
    - opacity: 0 (transparent) à 1 (opaque)
    - animation: type d’animation ('fade', 'slide'), progress: 0 (début) à 1 (fin)
    """
    pil_im = Image.fromarray(frame).convert("RGBA")
    txt_layer = Image.new("RGBA", pil_im.size, (255,255,255,0))
    draw = ImageDraw.Draw(txt_layer)
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    x, y, w, h = box
    w_text, h_text = draw.textsize(text, font=font)
    if w_text > w:
        font = ImageFont.truetype(font_path, max(12, int(font_size * w / w_text)))
        w_text, h_text = draw.textsize(text, font=font)

    # Animation : fade (opacity dynamique)
    if animation == 'fade':
        effective_opacity = int(255 * opacity * progress)
    else:
        effective_opacity = int(255 * opacity)
    # Animation : slide (texte qui "glisse" à l’apparition)
    if animation == 'slide':
        slide_offset = int((1.0 - progress) * w)
        x = x - slide_offset

    draw.text((x, y), text, font=font, fill=color + (effective_opacity,))
    overlaid = Image.alpha_composite(pil_im, txt_layer)
    return np.array(overlaid.convert("RGB"))

def edit_video_with_translations(
    video_path,
    ocr_boxes,
    trad_blocs,
    out_path="video_edited.mp4",
    lang="en",
    overlay_timing=None,
    overlay_opacity=0.85,
    overlay_animation="fade"
):
    clip = mp.VideoFileClip(video_path)
    frames = []
    fps = clip.fps

    for idx, frame in enumerate(clip.iter_frames()):
        overlays = [b for b in ocr_boxes if b["frame"] == idx]
        frame_out = frame.copy()
        for i, b in enumerate(overlays):
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            x, y, w, h = b["box"]
            mask[y:y+h, x:x+w] = 255
            frame_out = inpaint_with_lama(frame_out, mask)
            trad = trad_blocs[i]
            text = trad.get(f"text_{lang}", trad.get("text"))
            color = LANG_COLORS.get(lang, (255,255,255))
            # Gestion du timing et de l’animation
            if overlay_timing and idx in overlay_timing:
                t_data = overlay_timing[idx]
                cur_time = idx / fps
                start, end = t_data["start"], t_data["end"]
                if not (start <= cur_time <= end):
                    continue
                # Calcule la progression pour l’animation (0→1 au début, 1→0 à la fin)
                fade_in = min(1.0, max(0.0, (cur_time-start)/0.5))   # 0.5s de fade-in
                fade_out = min(1.0, max(0.0, (end-cur_time)/0.5))    # 0.5s de fade-out
                progress = min(fade_in, fade_out)
            else:
                progress = 1.0
            frame_out = overlay_text(
                frame_out,
                text,
                b["box"],
                color=color,
                opacity=overlay_opacity,
                animation=overlay_animation,
                progress=progress
            )
        frames.append(frame_out)
    new_clip = mp.ImageSequenceClip(frames, fps=fps)
    new_clip.write_videofile(out_path, audio=True)

# Utilisation :
# edit_video_with_translations(
#     "input.mp4", ocr_boxes, trad_blocs,
#     out_path="output.mp4", lang="es",
#     overlay_timing=timing_dict, overlay_opacity=0.85, overlay_animation="fade"
# )