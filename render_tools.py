import json
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip, ColorClip

def render_translated_video(input_video, script_json, lang, output_path):
    clip = VideoFileClip(input_video)
    txt_clips = []

    with open(script_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    for block in data["texts"]:
        start, end = block["start"], block["end"]
        text = block.get(f"text_{lang}", block["text"])
        x, y, w, h = block["bbox"]
        font_size = block.get("style", {}).get("font_size", 32)

        # Fond noir légèrement plus grand, semi-transparent
        bg = (ColorClip((w+10, h+10), color=(0,0,0))
              .set_opacity(0.6)
              .set_position((x-5, y-5))
              .set_duration(end - start)
              .set_start(start))

        # Overlay texte centré verticalement dans la bbox
        txt = (TextClip(text, fontsize=font_size, color="white", method="caption", size=(w, h), align="center")
               .set_position((x, y))
               .set_duration(end - start)
               .set_start(start))

        txt_clips.extend([bg, txt])

    final = CompositeVideoClip([clip] + txt_clips)
    final.write_videofile(output_path, codec="libx264", audio_codec="aac")