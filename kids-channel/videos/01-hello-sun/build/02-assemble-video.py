#!/usr/bin/env python3
"""Assemble the final MP4: 6 zoompan segments + 0.8s xfades on musical phrase
boundaries + fades + score. 1920x1080, 30fps, H.264 + AAC."""
import json
import subprocess

A = 'assets/'
SEGS = [
    # (image, padded_dur, zoom_dir)  -- padded +0.8s for segs 0..4 so xfades land on phrase bounds
    (A + 'media-generation-sensory-title-card-0-839e3056-eaf3-4c68-b8c0-351cf1f4ef5f.webp', 11.235, 'in'),
    (A + 'media-generation-sensory-dancing-sun-0-f8467bab-9f86-4b39-a267-faffe25adb47.webp', 21.669, 'out'),
    (A + 'media-generation-sensory-eye-tracking-0-e327b94b-41d4-44cc-993e-b27210413663.webp', 21.670, 'in'),
    (A + 'media-generation-sensory-shapes-ensemble-0-fa87931c-0fc0-47c1-80da-d8eae7c795fc.webp', 32.104, 'out'),
    (A + 'media-generation-sensory-scene4-reset-0-c0863353-f8f8-41cf-b6e1-5f6ea4908256.webp', 32.105, 'in'),
    (A + 'media-generation-sensory-title-card-0-839e3056-eaf3-4c68-b8c0-351cf1f4ef5f.webp', 50.934, 'out'),
]
FPS = 30
XF = 0.8
TOTAL = 165.717

cmd = ['ffmpeg', '-y']
for img, dur, _ in SEGS:
    cmd += ['-loop', '1', '-t', f'{dur:.3f}', '-i', img]
cmd += ['-i', 'build/score.wav']

fc = []
for i, (img, dur, zd) in enumerate(SEGS):
    frames = int(round(dur * FPS))
    if zd == 'in':
        z = f'1+0.10*on/{frames}'
    else:
        z = f'1.10-0.10*on/{frames}'
    fc.append(
        f'[{i}:v]scale=2400:1600:force_original_aspect_ratio=increase,'
        f'crop=2400:1600,'
        f'zoompan=z=\'{z}\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':'
        f'd={frames}:s=1920x1080:fps={FPS},setsar=1[v{i}]'
    )

# xfade chain; offsets land exactly on musical phrase boundaries
off = 0.0
prev = 'v0'
for k in range(1, 6):
    off += SEGS[k - 1][1] - XF
    out = f'x{k}'
    fc.append(f'[{prev}][v{k}]xfade=transition=fade:duration={XF}:offset={off:.3f}[{out}]')
    prev = out

fc.append(f'[{prev}]fade=t=in:st=0:d=0.6,fade=t=out:st={TOTAL-2:.3f}:d=2.0,format=yuv420p[vout]')

cmd += ['-filter_complex', ';'.join(fc),
        '-map', '[vout]', '-map', '6:a',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
        '-c:a', 'aac', '-b:a', '192k',
        '-t', f'{TOTAL:.3f}', '-movflags', '+faststart',
        'build/hello-sun-v1.mp4']
print(' '.join(cmd[:6]), '...', f'({len(cmd)} args)')
r = subprocess.run(cmd, capture_output=True, text=True)
print(r.stdout[-1500:] if r.stdout else '')
print(r.stderr[-3000:] if r.stderr else '')
print('returncode:', r.returncode)
