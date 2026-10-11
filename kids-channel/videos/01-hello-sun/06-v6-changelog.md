# Video #1 "Hello, Sun!" — v6 Final Changelog (Broadcast quality)

**Build:** `build/09-assemble-v6.py`
**Video:** `build/v4_frames/` (v3 supersampled + Pip & Ducky hosts)
**Audio:** `build/score-v5.wav` (music-box score + 5 vocal lines)
**Output:** `hello-sun-v6-final.mp4` — 1920x1080, 30fps, H.264 + AAC 192k

## What v6 combines

### v3 — Polish pass (Grok binding)
- 2x supersampling (3200x1800 → 1600x900 LANCZOS)
- Uniform 3px strokes on all shapes
- 2-frame ground crossfades
- Beat-grid aligned (max drift 15.9ms, inherent to 30fps)

### v4 — Character animation (Grok binding)
- Pip & Ducky as strict hosts on cream panels, lower third
- 5 appearances × 4 beats, static poses (no tweening)
- Zero hero-sun occlusion

### v5 — Vocals (Grok binding)
- 5 gentle lines, dry, no reverb (voice: Isabella / Soothing Ribbon)
- "Hello, sun!" (bar 1) / "Up we go." (bar 9) / "Big and bright." (bar 17)
  "Wave hello." (bar 25) / "Goodnight, sun." (bar 33)
- Locked to woodblock downbeats, -18 LUFS target

## Grok vetoes honored
- No physics/secondary motion on characters (static holds only)
- No added instruments, pads, or melodic vocals
- No runtime change (2:45), no extra layers

## Version history
- v1: Initial sensory build
- v2: Grok review (14 fixes — hook, palette, motion, audio layers)
- v3: Polish (supersample, strokes, crossfades)
- v4: Character hosts
- v5: Vocal narration
- v6: Final assembly — broadcast quality
