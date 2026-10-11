#!/usr/bin/env python3
"""Assemble v6: v4 frames (v3 + characters) + v5 audio (score + vocals).
Output: hello-sun-v6-final.mp4 — 1920x1080, 30fps, H.264 + AAC."""
import subprocess, os

VDIR = 'build/v4_frames'
AUDIO = 'build/score-v5.wav'
OUT = 'hello-sun-v6-final.mp4'

# get audio duration to set exact length
r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                    '-of', 'csv=p=0', AUDIO], capture_output=True, text=True)
dur = float(r.stdout.strip())
print(f'audio duration: {dur:.2f}s', flush=True)

# count frames
nframes = len([f for f in os.listdir(VDIR) if f.endswith('.png')])
print(f'frames: {nframes}', flush=True)

subprocess.run([
    'ffmpeg', '-y', '-v', 'error',
    '-framerate', '30', '-i', f'{VDIR}/fr_%05d.png',
    '-i', AUDIO,
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
    '-pix_fmt', 'yuv420p',
    '-vf', 'scale=1920:1080',
    '-c:a', 'aac', '-b:a', '192k',
    # NOTE: no -shortest — it trimmed the final frame (4971 vs 4972).
    # Video (4972f = 165.733s) is the authority; audio (165.717s) ends 16ms early.
    '-movflags', '+faststart',
    OUT
], check=True)
print(f'wrote {OUT}', flush=True)
