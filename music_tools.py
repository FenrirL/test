from moviepy.editor import AudioFileClip, VideoFileClip, CompositeAudioClip
from moviepy.audio.fx.all import audio_fadein, audio_fadeout

def add_music(video_path, music_path, output_path, music_volume=0.2, fadein=2, fadeout=2):
    video = VideoFileClip(video_path)
    original_audio = video.audio
    music = AudioFileClip(music_path).subclip(0, video.duration)
    music = audio_fadein(music.volumex(music_volume), fadein)
    music = audio_fadeout(music, fadeout)
    final_audio = CompositeAudioClip([original_audio, music])
    final_video = video.set_audio(final_audio)
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
    video.close()
    music.close()
    final_audio.close()
    final_video.close()