from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip

def render_translated_video(input_path, script_path, lang_code, output_path, mask_expand=1.2):
    # TODO: inpainting avancé, flou adaptatif, watermark/outro...
    import json
    with open(script_path, encoding="utf-8") as f:
        data = json.load(f)
    clip = VideoFileClip(input_path)
    overlays = []
    for block in data.get("texts", []):
        txt = block.get(f"text_{lang_code}") or block.get("text")
        x, y, w, h = block["bbox"]
        # Agrandit le masque
        cx, cy = x + w//2, y + h//2
        w2, h2 = int(w*mask_expand), int(h*mask_expand)
        x2, y2 = max(0, cx - w2//2), max(0, cy - h2//2)
        start, end = block["start"], block["end"]
        mask_clip = ColorClip(size=(w2, h2), color=(0,0,0)).set_opacity(0.7).set_start(start).set_duration(end-start).set_position((x2, y2))
        txt_clip = TextClip(txt, fontsize=32, color="#FFFFFF", size=(w2, h2), method='caption').set_start(start).set_duration(end-start).set_position((x2, y2))
        overlays.extend([mask_clip, txt_clip])
    # TODO: add thumbnail, outro, watermark
    final = CompositeVideoClip([clip] + overlays)
    final.write_videofile(output_path, codec="libx264", audio_codec="aac")
    clip.close()