#!/usr/bin/env python3
"""Assemble v3 draft: v3 frames + score-v2.wav (no vocals yet).
Picture-lock QC draft."""
import subprocess, os

VDIR = 'build/v3_frames'
AUDIO = 'build/score-v2.wav'
OUT = 'build/hello-sun-v3-draft.mp4'

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
    '-shortest',
    '-movflags', '+faststart',
    OUT
], check=True)
print(f'wrote {OUT}', flush=True)
