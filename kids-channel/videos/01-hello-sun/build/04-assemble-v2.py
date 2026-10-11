#!/usr/bin/env python3
"""Assemble v2 final MP4: PNG sequence (1600x900@30) -> 1920x1080 + score-v2.wav."""
import subprocess

TOTAL = 165.717
cmd = [
    'ffmpeg', '-y',
    '-framerate', '30', '-i', 'build/v2_frames/fr_%05d.png',
    '-i', 'build/score-v2.wav',
    '-filter_complex',
    f'[0:v]scale=1920:1080:flags=lanczos,fade=t=in:st=0:d=0.6,'
    f'fade=t=out:st={TOTAL-2:.3f}:d=2.0,format=yuv420p[vout]',
    '-map', '[vout]', '-map', '1:a',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
    '-c:a', 'aac', '-b:a', '192k',
    '-t', f'{TOTAL:.3f}', '-movflags', '+faststart',
    'hello-sun-v2-final.mp4',
]
r = subprocess.run(cmd, capture_output=True, text=True)
print(r.stderr[-2000:] if r.stderr else r.stdout[-1000:])
print('returncode:', r.returncode)
