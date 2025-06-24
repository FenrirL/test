from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, vfx

def add_watermark(clip, text="via MyPipeline"):
    txt = TextClip(text, fontsize=20, color='white', font='DejaVu-Sans')
    txt = txt.set_pos(("right", "bottom")).set_duration(clip.duration)
    return CompositeVideoClip([clip, txt])