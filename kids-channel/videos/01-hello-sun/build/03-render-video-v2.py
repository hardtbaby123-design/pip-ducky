#!/usr/bin/env python3
"""Hello, Sun! v2 frame renderer — per-shape animated vector scenes (Grok review).
1600x900 @30fps, PIL. Outputs build/v2_frames -> assembled by 04 script."""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1600, 900, 30
BEAT = 60.0 / 92.0
TOTAL = 165.717
NFRAMES = int(round(TOTAL * FPS))
OUTDIR = 'build/v2_frames'

# ---- tempo map (mirror of audio script) ----
beat_t = []
t = 0.0
for bar in range(62):
    bd = BEAT if bar < 58 else BEAT * (1.0 + 0.25 * (bar - 58) / 4.0)
    for _ in range(4):
        beat_t.append(t)
        t += bd
def bar_start(b):
    return beat_t[b * 4]

# ---- palette ----
BLACK, WHITE = (0, 0, 0), (255, 255, 255)
YELLOW = (255, 212, 0)
RED = (255, 59, 92)
BLUE = (30, 107, 255)
MINT = (46, 196, 182)
DARK = (17, 17, 17)

# ---- events: (start_bar, end_bar, ground, kind) ----
EVENTS = [
    (0, 4, 'B', 'title'),
    (4, 7, 'B', 'suns'),
    (7, 10, 'W', 'mixed'),
    (10, 12, 'B', 'redblue'),
    (12, 15, 'W', 'mixed2'),
    (15, 18, 'B', 'ensemble'),
    (18, 20, 'W', 'diamonds'),
    (20, 23, 'B', 'peak'),
    (23, 26, 'W', 'mixed3'),
    (26, 29, 'B', 'orbit'),
    (29, 32, 'W', 'reset'),
    (32, 35, 'B', 'rects'),
    (35, 38, 'W', 'bluedense'),
    (38, 41, 'B', 'mix4'),
    (41, 44, 'W', 'soft'),
    (44, 47, 'B', 'finale'),
    (47, 50, 'W', 'bright'),
    (50, 53, 'B', 'grow'),
    (53, 56, 'W', 'drift'),
    (56, 58, 'B', 'prefinale'),
    (58, 62, 'B', 'resolve'),
]
EV_START = [bar_start(s) for s, e, g, k in EVENTS]
EV_END = [bar_start(e) if e <= 58 else None for s, e, g, k in EVENTS]
# bar 62 end: compute like audio END_T
EV_END[-1] = TOTAL

SPRITES = {}
def sprite(kind, size, fill, outline, ow, eyes=False):
    key = (kind, size, fill, outline, ow, eyes)
    if key in SPRITES:
        return SPRITES[key]
    pad = int(ow + size * 0.3) + 8
    S = int(size + pad * 2)
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    r = size / 2
    if kind == 'circle':
        d.ellipse([c - r - ow, c - r - ow, c + r + ow, c + r + ow], fill=outline + (255,))
        d.ellipse([c - r, c - r, c + r, c + r], fill=fill + (255,))
    elif kind == 'sun':
        # white ring + yellow disc
        d.ellipse([c - r - ow, c - r - ow, c + r + ow, c + r + ow], fill=(255, 255, 255, 255))
        d.ellipse([c - r, c - r, c + r, c + r], fill=fill + (255,))
        if eyes:
            er = r * 0.11
            for sx in (-r * 0.32, r * 0.32):
                d.ellipse([c + sx - er, c - r * 0.1 - er, c + sx + er, c - r * 0.1 + er],
                          fill=(10, 10, 10, 255))
    elif kind == 'triangle':
        pts = [(c, c - r * 1.15), (c - r, c + r * 0.85), (c + r, c + r * 0.85)]
        d.polygon(pts, fill=fill + (255,), outline=outline + (255,), width=int(ow))
    elif kind == 'diamond':
        pts = [(c, c - r * 1.2), (c + r * 0.9, c), (c, c + r * 1.2), (c - r * 0.9, c)]
        d.polygon(pts, fill=fill + (255,), outline=outline + (255,), width=int(ow))
    elif kind == 'rect':
        d.rounded_rectangle([c - r * 1.3 - ow, c - r * 0.7 - ow, c + r * 1.3 + ow, c + r * 0.7 + ow],
                            radius=int(r * 0.5), fill=outline + (255,))
        d.rounded_rectangle([c - r * 1.3, c - r * 0.7, c + r * 1.3, c + r * 0.7],
                            radius=int(r * 0.45), fill=fill + (255,))
    SPRITES[key] = (im, pad)
    return SPRITES[key]

def ease_out_back(x):
    x = max(0.0, min(1.0, x))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def gen_event(idx):
    rng = random.Random(1000 + idx)
    s_bar, e_bar, ground, kind = EVENTS[idx]
    bg = BLACK if ground == 'B' else WHITE
    ol = WHITE if ground == 'B' else DARK
    shapes = []
    cx, cy = W * 0.5, H * 0.44

    def add(kind_, size, fill, x, y, hero=False, orbit=None, grow_to=None):
        shapes.append({
            'kind': kind_, 'size': size, 'fill': fill, 'ol': ol,
            'ow': 10, 'x': x, 'y': y,
            'phase': rng.uniform(0, 2 * math.pi),
            'dphi1': rng.uniform(0, 2 * math.pi), 'dphi2': rng.uniform(0, 2 * math.pi),
            'rot0': 0 if hero else rng.uniform(0, 360), 'rotdir': rng.choice([-1, 1]),
            'rotspeed': 0 if hero else rng.uniform(0.3, 0.5),
            'stagger': len(shapes) * 1.5,
            'hero': hero, 'orbit': orbit, 'grow_to': grow_to,
        })

    if kind in ('title', 'resolve'):
        # hero sun fully visible top-center (the "face"), text below it
        add('sun', 400, YELLOW, cx, 250, hero=True)
        for i in range(6):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(300, 420)
            sz = rng.uniform(80, 130)
            add(rng.choice(['circle', 'triangle', 'diamond']),
                sz, rng.choice([RED, BLUE, MINT]),
                cx + rr * math.cos(a) * 1.6, 620 + rr * math.sin(a) * 0.45)
    elif kind == 'suns':
        add('sun', 300, YELLOW, cx, cy, hero=True)
        for i in range(7):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(300, 480)
            add('circle', rng.uniform(70, 150), YELLOW,
                cx + rr * math.cos(a) * 1.5, cy + rr * math.sin(a) * 0.85)
    elif kind in ('mixed', 'mixed2', 'mixed3', 'mix4'):
        cols = [YELLOW, RED, BLUE]
        add('sun', 280, YELLOW, cx, cy, hero=True)
        target = 0.48 * W * H
        area = math.pi * 140 ** 2
        kinds = ['circle', 'triangle', 'diamond', 'rect']
        tries = 0
        while area < target and tries < 200:
            tries += 1
            k = rng.choice(kinds)
            sz = rng.uniform(70, 200)
            col = rng.choice(cols + ([MINT] if rng.random() < 0.12 else []))
            x = rng.uniform(120, W - 120)
            y = rng.uniform(100, H - 100)
            ok = all(math.hypot(x - s['x'], y - s['y']) > (sz + s['size']) * 0.32 for s in shapes)
            if not ok:
                continue
            add(k, sz, col, x, y)
            area += math.pi * (sz / 2) ** 2
    elif kind == 'redblue':
        add('sun', 260, YELLOW, cx, cy, hero=True)
        for i in range(9):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(260, 470)
            add('circle', rng.uniform(80, 170), rng.choice([RED, BLUE]),
                cx + rr * math.cos(a) * 1.5, cy + rr * math.sin(a) * 0.85)
    elif kind == 'ensemble':
        add('sun', 300, YELLOW, cx, cy, hero=True)
        cols = [YELLOW, RED, BLUE, RED, BLUE, YELLOW]
        for i in range(12):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(280, 500)
            add(rng.choice(['circle', 'triangle', 'diamond', 'rect']),
                rng.uniform(70, 180), cols[i % len(cols)],
                cx + rr * math.cos(a) * 1.5, cy + rr * math.sin(a) * 0.85)
    elif kind == 'diamonds':
        add('sun', 240, YELLOW, cx, cy, hero=True)
        for i in range(11):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(240, 470)
            add('diamond', rng.uniform(80, 190), rng.choice([BLUE, YELLOW, RED]),
                cx + rr * math.cos(a) * 1.5, cy + rr * math.sin(a) * 0.85)
    elif kind == 'peak':
        add('sun', 400, YELLOW, cx, cy, hero=True)
        for i in range(12):
            a = i / 12 * 2 * math.pi
            rr = rng.uniform(380, 520)
            add(rng.choice(['circle', 'triangle', 'diamond']),
                rng.uniform(80, 170), rng.choice([RED, BLUE, YELLOW]),
                cx + rr * math.cos(a) * 1.45, cy + rr * math.sin(a) * 0.8)
    elif kind == 'orbit':
        add('sun', 300, YELLOW, cx, cy, hero=True)
        for i in range(8):
            add(rng.choice(['circle', 'diamond', 'triangle']),
                rng.uniform(70, 140), rng.choice([RED, BLUE, YELLOW]),
                cx, cy, orbit={'rx': rng.uniform(280, 480), 'ry': rng.uniform(170, 260),
                               'T': rng.uniform(4, 6), 'p0': rng.uniform(0, 2 * math.pi)})
    elif kind == 'reset':
        add('sun', 250, YELLOW, cx, cy, hero=True)
        for i in range(9):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(260, 470)
            add(rng.choice(['circle', 'rect']), rng.uniform(70, 160),
                rng.choice([MINT, BLUE, YELLOW]),
                cx + rr * math.cos(a) * 1.5, cy + rr * math.sin(a) * 0.85)
    elif kind == 'rects':
        add('sun', 270, YELLOW, cx, cy, hero=True)
        for i in range(10):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(270, 480)
            add('rect', rng.uniform(90, 200), RED,
                cx + rr * math.cos(a) * 1.5, cy + rr * math.sin(a) * 0.85)
    elif kind == 'bluedense':
        add('sun', 250, YELLOW, cx, cy, hero=True)
        for i in range(11):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(250, 470)
            add('diamond', rng.uniform(90, 200), BLUE,
                cx + rr * math.cos(a) * 1.5, cy + rr * math.sin(a) * 0.85)
    elif kind == 'soft':
        add('sun', 260, YELLOW, cx, cy, hero=True)
        for i in range(8):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(270, 470)
            add(rng.choice(['circle', 'triangle']), rng.uniform(70, 150),
                rng.choice([MINT, BLUE, YELLOW]),
                cx + rr * math.cos(a) * 1.5, cy + rr * math.sin(a) * 0.85)
    elif kind == 'finale':
        add('sun', 330, YELLOW, cx, cy, hero=True)
        for i in range(13):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(300, 510)
            add(rng.choice(['circle', 'triangle', 'diamond', 'rect']),
                rng.uniform(80, 190), rng.choice([YELLOW, RED, BLUE]),
                cx + rr * math.cos(a) * 1.5, cy + rr * math.sin(a) * 0.85)
    elif kind == 'bright':
        add('sun', 280, YELLOW, cx, cy, hero=True)
        for i in range(10):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(270, 480)
            add(rng.choice(['circle', 'diamond']), rng.uniform(80, 180),
                rng.choice([YELLOW, RED]),
                cx + rr * math.cos(a) * 1.5, cy + rr * math.sin(a) * 0.85)
    elif kind == 'grow':
        add('sun', 280, YELLOW, cx, cy, hero=True, grow_to=1.6)
        for i in range(8):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(300, 500)
            add('circle', rng.uniform(70, 150), rng.choice([RED, BLUE, YELLOW]),
                cx + rr * math.cos(a) * 1.5, cy + rr * math.sin(a) * 0.85)
    elif kind == 'drift':
        add('sun', 270, YELLOW, cx, cy, hero=True)
        for i in range(9):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(270, 480)
            add(rng.choice(['triangle', 'diamond', 'rect']), rng.uniform(70, 170),
                rng.choice([BLUE, RED, MINT, YELLOW]),
                cx + rr * math.cos(a) * 1.5, cy + rr * math.sin(a) * 0.85)
    elif kind == 'prefinale':
        add('sun', 320, YELLOW, cx, cy, hero=True)
        for i in range(10):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(300, 500)
            add('circle', rng.uniform(80, 170), rng.choice([YELLOW, RED, BLUE]),
                cx + rr * math.cos(a) * 1.5, cy + rr * math.sin(a) * 0.85)

    # coverage enforcement: HONEST pixel measurement (Grok round 2).
    # Content plates must hit >=55% total fill AND >=30% in every 3x2 cell.
    import numpy as _np
    def _measure():
        gw, gh = 160, 90  # 10px cells
        grid = _np.zeros((gh, gw), dtype=_np.float32)
        yy, xx = _np.mgrid[0:gh, 0:gw]
        for s in shapes:
            r = (s['size'] / 2) * 0.8 / 10.0  # conservative disc, in cells
            cxg, cyg = s['x'] / 10.0, s['y'] / 10.0
            d2 = (xx - cxg) ** 2 + (yy - cyg) ** 2
            grid[d2 <= r * r] = 1.0
        total = float(grid.mean())
        cells = []
        for cr in range(2):
            for cc in range(3):
                cells.append(float(grid[cr * 45:(cr + 1) * 45, cc * 53:(cc + 1) * 54].mean()))
        return total, cells

    if kind not in ('title', 'resolve'):
        guard = 0
        while guard < 120:
            cov, cells = _measure()
            if cov >= 0.55 and all(c >= 0.30 for c in cells):
                break
            guard += 1
            # target the emptiest cell
            ei = int(_np.argmin(cells))
            er, ec = ei // 3, ei % 3
            k = rng.choice(['circle', 'triangle', 'diamond', 'rect'])
            sz = rng.uniform(140, 280)
            col = rng.choice([YELLOW, RED, BLUE] + ([MINT] if rng.random() < 0.1 else []))
            best, bestd = None, -1
            for _ in range(20):
                x = rng.uniform(ec * 533 + 90, (ec + 1) * 533 - 90)
                y = rng.uniform(er * 450 + 80, (er + 1) * 450 - 80)
                md = min([math.hypot(x - s['x'], y - s['y']) for s in shapes] or [1e9])
                if md > bestd:
                    bestd, best = md, (x, y)
            if bestd < 60:
                continue
            add(k, sz, col, best[0], best[1])
        cov, cells = _measure()
        print(f'event {idx} ({kind}): coverage={cov:.2f} cells={[round(c,2) for c in cells]} '
              f'shapes={len(shapes)}', flush=True)

    # clamp into safe margin
    for s in shapes:
        m = 60 + s['size'] / 2
        s['x'] = max(m, min(W - m, s['x']))
        s['y'] = max(m, min(H - m, s['y']))
    return {'bg': bg, 'ground': ground, 'kind': kind, 'shapes': shapes,
            't0': EV_START[idx], 't1': EV_END[idx]}

EVENTS_R = [gen_event(i) for i in range(len(EVENTS))]
print(f'generated {len(EVENTS_R)} events', flush=True)

FONT_BIG = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 215)
FONT_TITLE = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 175)
FONT_SM = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 54)

def draw_title(img, t, hero_pulse):
    d = ImageDraw.Draw(img)
    cx = W / 2
    # text sits BELOW the fully-visible hero sun (Grok #3)
    for txt, y in (('HELLO,', 490), ('SUN!', 655)):
        d.text((cx, y), txt, font=FONT_TITLE, fill=(255, 255, 255),
               anchor='ma', stroke_width=9, stroke_fill=(0, 0, 0))
    d.text((cx, H - 45), 'Pip & Ducky', font=FONT_SM, fill=(255, 255, 255, 200), anchor='ma')

os.makedirs(OUTDIR, exist_ok=True)
BLEND = 12  # bg crossfade frames

F_START = int(sys.argv[1]) if len(sys.argv) > 1 else 0
F_END = int(sys.argv[2]) if len(sys.argv) > 2 else NFRAMES

for f in range(F_START, min(F_END, NFRAMES)):
    t = f / FPS
    # find event
    ei = 0
    for i, ev in enumerate(EVENTS_R):
        if t < ev['t1']:
            ei = i
            break
        ei = i
    ev = EVENTS_R[ei]
    evf0 = int(round(ev['t0'] * FPS))
    evf1 = int(round(ev['t1'] * FPS))

    # background (blend across boundary)
    bg = ev['bg']
    if f - evf0 < BLEND and ei > 0:
        prev = EVENTS_R[ei - 1]['bg']
        a = (f - evf0) / BLEND
        bg = tuple(int(prev[c] * (1 - a) + bg[c] * a) for c in range(3))
    img = Image.new('RGB', (W, H), bg)

    # draw shapes of current event (+ previous during blend for pop-out)
    draw_list = []
    for e2, is_prev in ((ev, False), (EVENTS_R[ei - 1], True) if (f - evf0 < BLEND and ei > 0) else (None, False)):
        if e2 is None:
            continue
        e2f0 = int(round(e2['t0'] * FPS))
        e2f1 = int(round(e2['t1'] * FPS))
        for s in e2['shapes']:
            draw_list.append((s, e2, is_prev, e2f0, e2f1))
    # small shapes first, hero last
    draw_list.sort(key=lambda x: (x[0]['hero'], x[0]['size']))

    for s, e2, is_prev, e2f0, e2f1 in draw_list:
        # pop in / out
        if is_prev:
            # fading out across the blend window
            pop = max(0.0, 1.0 - (f - e2f1) / BLEND)
        else:
            lp = f - e2f0 - s['stagger']
            pop = ease_out_back(lp / 9) if lp < 9 else 1.0
            lo = e2f1 - f
            if lo < 9 and not (f - evf0 < BLEND):
                pop *= max(0.0, lo / 9)
        if pop <= 0.01:
            continue
        pulse = 1 + 0.07 * math.sin(2 * math.pi * (92 / 60) * t + s['phase'])
        if s['hero'] and e2['kind'] in ('title', 'resolve'):
            pulse = 1 + 0.06 + 0.06 * math.sin(2 * math.pi * (92 / 60) * t + s['phase'])
        grow = 1.0
        if s.get('grow_to'):
            gp = max(0.0, min(1.0, (t - e2['t0']) / (e2['t1'] - e2['t0'])))
            grow = 1 + (s['grow_to'] - 1) * gp
        scale = pop * pulse * grow
        # position + drift / orbit
        if s.get('orbit'):
            o = s['orbit']
            ang = o['p0'] + 2 * math.pi * (t - e2['t0']) / o['T']
            x = W / 2 + o['rx'] * math.cos(ang)
            y = H * 0.44 + o['ry'] * math.sin(ang)
        else:
            x = s['x'] + 15 * math.sin(2 * math.pi * 0.11 * t + s['dphi1'])
            y = s['y'] + 12 * math.cos(2 * math.pi * 0.09 * t + s['dphi2'])
        angle = s['rot0'] + s['rotdir'] * s['rotspeed'] * (t - e2['t0'])
        # eyes on hero sun: always on title/resolve (the channel "face"),
        # else the 22s reset. Hero never rotates so eyes stay level (Grok #1).
        eyes = (s['hero'] and (e2['kind'] in ('title', 'resolve')
                               or (t % 22.0) < 2.0))
        spr, pad = sprite(s['kind'], s['size'], s['fill'], s['ol'], s['ow'], eyes=eyes)
        rot = spr.rotate(angle, expand=True, resample=Image.BICUBIC)
        nw = max(1, int(rot.width * scale))
        nh = max(1, int(rot.height * scale))
        if nw < 4 or nh < 4:
            continue
        rot = rot.resize((nw, nh), Image.BICUBIC)
        img.paste(rot, (int(x - nw / 2), int(y - nh / 2)), rot)

    if ev['kind'] in ('title', 'resolve'):
        draw_title(img, t, True)

    img.save(f'{OUTDIR}/fr_{f:05d}.png')
    if f % 600 == 0:
        print(f'frame {f}/{NFRAMES}', flush=True)

print('render done', flush=True)
