from moviepy.editor import VideoFileClip

def generate_thumbnail(video_path, output_image, t=None):
    """
    Génère une miniature à un moment fort (t ou frame max OCR).
    """
    video = VideoFileClip(video_path)
    if t is None:
        t = video.duration // 2
    frame = video.get_frame(t)
    from PIL import Image
    img = Image.fromarray(frame)
    img.save(output_image)
    video.close()