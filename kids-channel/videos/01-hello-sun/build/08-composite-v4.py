#!/usr/bin/env python3
"""Hello, Sun! v4 — composite Pip & Ducky character hosts onto v3 frames.
Grok binding: characters are strict hosts, lower third, cream panels,
enter on downbeat of events 4,8,12,16,20 (1-indexed), one static pose
for exactly 4 beats, then exit. No tweening, no overlap with hero sun."""
import math, os
from PIL import Image, ImageDraw

BEAT = 60.0 / 92.0
FPS = 30
FOUR_BEATS_F = int(round(4 * BEAT * FPS))  # 78 frames
FADE = 6

# tempo map (mirror)
beat_t = []
t = 0.0
for bar in range(62):
    bd = BEAT if bar < 58 else BEAT * (1.0 + 0.25 * (bar - 58) / 4.0)
    for _ in range(4):
        beat_t.append(t)
        t += bd

# (event_bar, pose_file)
APPEARANCES = [
    (4, 'pip_wave'),
    (18, 'ducky_splash'),
    (35, 'pip_armsup'),
    (44, 'ducky_wave'),
    (53, 'pip_point'),
]

CREAM = (253, 242, 226)
# v4 spec (binding): panel 440x320, bottom-center, top edge y=565.
# Rounded rectangle r=36, character scaled to ~260px tall, centered.
PANEL_W, PANEL_H = 440, 320
RADIUS = 36
PANEL_TOP_Y = 565
CHAR_H = 260

def make_panel(pose_path):
    """Build a cream rounded panel with the pose centered."""
    pose = Image.open(f'build/poses/{pose_path}.png').convert('RGB')
    pw, ph = pose.size
    scale = CHAR_H / ph
    nw, nh = int(pw * scale), int(ph * scale)
    pose = pose.resize((nw, nh), Image.LANCZOS)
    # base panel
    panel = Image.new('RGB', (PANEL_W, PANEL_H), CREAM)
    panel.paste(pose, ((PANEL_W - nw) // 2, (PANEL_H - nh) // 2))
    # rounded mask applied AFTER pose paste
    mask = Image.new('L', (PANEL_W, PANEL_H), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, PANEL_W, PANEL_H], radius=RADIUS, fill=255)
    out = Image.new('RGBA', (PANEL_W, PANEL_H), (0, 0, 0, 0))
    out.paste(panel, (0, 0))
    out.putalpha(mask)
    return out

panels = {name: make_panel(name) for _, name in APPEARANCES}
print('panels built', flush=True)

IN_DIR = 'build/v3_frames'
OUT_DIR = 'build/v4_frames'
os.makedirs(OUT_DIR, exist_ok=True)

NFRAMES = len([f for f in os.listdir(IN_DIR) if f.endswith('.png')])
print(f'compositing {NFRAMES} frames', flush=True)

# frame range override for parallel compositing: F0 F1 env vars
F_START = int(os.environ.get('F0', 0))
F_END = int(os.environ.get('F1', NFRAMES))
print(f'compositing frames {F_START}..{F_END}', flush=True)

# precompute appearance frame ranges
apps = []
for bar, name in APPEARANCES:
    f0 = int(round(beat_t[bar * 4] * FPS))
    apps.append((f0, f0 + FOUR_BEATS_F, panels[name]))

for f in range(F_START, F_END):
    # skip if already done
    _out = f'{OUT_DIR}/fr_{f:05d}.png'
    if os.path.exists(_out):
        continue
    frame = Image.open(f'{IN_DIR}/fr_{f:05d}.png').convert('RGBA')
    W, H = frame.size
    # v4 spec (binding): bottom-center, top edge at y=565 — hero sun eyes at
    # y=396 always clear. (1920x1080: px = (1920-440)//2 = 740.)
    px, py = (W - PANEL_W) // 2, PANEL_TOP_Y

    for f0, f1, panel in apps:
        if f0 <= f < f1:
            lf = f - f0
            # fade in/out
            if lf < FADE:
                alpha = lf / FADE
            elif f1 - f <= FADE:
                alpha = max(0.0, (f1 - f) / FADE)
            else:
                alpha = 1.0
            if alpha > 0.01:
                p = panel.copy()
                # apply alpha
                a = p.split()[3].point(lambda v: int(v * alpha))
                p.putalpha(a)
                frame.paste(p, (px, py), p)
            break  # only one appearance at a time

    frame.convert('RGB').save(f'{OUT_DIR}/fr_{f:05d}.png')
    if f % 600 == 0:
        print(f'frame {f}/{NFRAMES}', flush=True)

print('v4 composite done', flush=True)
