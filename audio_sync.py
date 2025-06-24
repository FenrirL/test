import os
import asyncio
from typing import List, Dict, Any, Optional
from moviepy.editor import VideoFileClip, AudioFileClip

def generate_tts_segments(text_blocks: List[Dict[str, Any]], lang: str) -> List[Dict[str, Any]]:
    tts_segments = []
    for block in text_blocks:
        tts_segments.append({
            "text": block["text"],
            "start": block["start"],
            "end": block["end"],
            "lang": lang,
        })
    return tts_segments

def align_overlay_timing_with_tts(tts_segments: List[Dict[str, Any]], overlays: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    aligned = []
    for seg, overlay in zip(tts_segments, overlays):
        aligned.append({
            **overlay,
            "start": seg["start"],
            "end": seg["end"],
        })
    return aligned

async def merge_audio_on_video(
    video_path: str,
    tts_audio_paths: List[str],
    segment_timings: List[Dict[str, Any]],
    out_path: str,
    music_path: Optional[str] = None
) -> None:
    video = VideoFileClip(video_path)
    tts_clips = []
    for seg, audio_path in zip(segment_timings, tts_audio_paths):
        tts_clip = AudioFileClip(audio_path).set_start(seg["start"])
        tts_clips.append(tts_clip)
    if tts_clips:
        from moviepy.audio.AudioClip import CompositeAudioClip
        tts_audio = CompositeAudioClip(tts_clips)
        if music_path:
            music = AudioFileClip(music_path).subclip(0, video.duration)
            final_audio = CompositeAudioClip([music, tts_audio])
        else:
            final_audio = tts_audio
        video = video.set_audio(final_audio)
    video.write_videofile(out_path, codec="libx264", audio_codec="aac")