# Video #1 "Hello, Sun!" — v2 Changelog (Grok review implemented)

**File out:** `hello-sun-v2-final.mp4` — 1920x1080, 30fps, H.264 + AAC 192k, 165.7s.
**Audio:** `build/score-v2.wav` — same length/tempo map as v1.

## Grok's v1 critique → v2 fix

| # | Grok's note | v2 implementation |
|---|-------------|-------------------|
| 1 | Gray title text loses 3-sec hook | Pure white `HELLO, SUN!` (DejaVu Bold, 215px) + 10px black stroke, giant yellow sun pulsing 1.00–1.12 behind `SUN!` |
| 2 | Muddy/olive shapes on title card | Full-saturation palette locked: `#FFD400` `#FF3B5C` `#1E6BFF`, mint `#2EC4B6` accent only |
| 3 | Static circles fatigue in ~20s holds | Per-shape beat pulse `1+0.07·sin(2π·92/60·t+φ)`, staggered phases, 10–20px drift |
| 4 | S2 = slideshow still, pastel-on-white | Replaced: 8–10 mixed black-outlined saturated shapes, 0.35x–1.6x sizes, ±15–35° rotation |
| 5 | No hierarchy / motion cue in ensemble | Hero sun (~35% frame height) in every event; smaller shapes orbit on 4–6s ellipses in E9 |
| 6 | Thin strokes vanish on white | 10px `#111` outlines on white-ground shapes; fills `#FF2D78`/`#005CFF`-class saturation |
| 7 | Dead regions, no edges to track | 45–60% shape coverage per plate, one focal cluster, 20px safe margin |
| 8 | Single zoom = PowerPoint feel | 3 stacked motions: beat pulse + 0.3–0.5°/s counter-rotation + sinusoidal drift; pop-in/out instead of hard cuts; 12-frame bg crossfades |
| 9 | Not enough novelty for 2:45 | 21 beat-snapped events (5–10s each), black/white grounds alternate, yellow sun threaded through all |
| 10 | Mint-as-hero fights attention | Mint demoted to rare accent |
| 11 | Flat music-box bed | Added: woodblock on beats 1&3, bell on each scene change, two-note chime in first second, register-lift sparkle arpeggio every 30s. Same C major / 92 BPM |
| 12 | Shapes fully on-screen at scene start | Pop-in over 9 frames with easeOutBack overshoot, staggered 1.5 frames; last 8s resolve to title card with musical cadence |
| 13 | Thumbnail ≠ video family | Thumbnail = v2 title frame (giant sun + white text); same sun asset in-video |
| 14 | Faceless retention risk | Non-character reset: two black dots ("eyes") inside hero sun for 2s every 22s |

## Build pipeline (v2, reproducible)
- `build/01b-synth-audio-v2.py` → `build/score-v2.wav` (extends v1 arrangement, identical length)
- `build/03-render-video-v2.py` → `build/v2_frames/fr_*.png` (PIL vector render, 1600x900 @30fps)
- `build/04-assemble-v2.py` → `hello-sun-v2-final.mp4` (ffmpeg: upscale 1920x1080, mux audio, fades)

## Deliberately kept from v1
- No vocals (still no real vocalist recorded — never faked)
- No AI-animated clips (vector motion is now the system)
- 2:45 runtime, same tempo map, same title
