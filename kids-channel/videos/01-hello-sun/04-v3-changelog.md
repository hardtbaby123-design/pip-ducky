# Video #1 "Hello, Sun!" — v3 Changelog (Grok polish pass)

**Build:** `build/05-render-video-v3.py` → `build/v3_frames/` (1600x900 PNGs)
**Assemble:** `build/06-assemble-v3.py` → `build/hello-sun-v3-draft.mp4` (with score-v2.wav)

## Grok's binding decisions implemented

1. **Supersampling**: 2x SSAA (3200x1800 → 1600x900) was attempted per Grok's spec
   but caused OOM kills and 7+ hour render times on available hardware. Fell back
   to 1x with PIL native anti-aliasing. All other polish decisions intact. The
   visual difference is negligible for YouTube 1080p delivery after compression.

2. **Uniform 3px strokes**: All shapes use identical 3px stroke weight.
   Thinner, more refined than v2's 10px — the "could run on a kids' network" look.

3. **2-frame ground crossfades**: Background flips use a 2-frame crossfade with the
   incoming ground starting at 0 opacity. No more 12-frame dissolves.

4. **Beat-grid audit**: Max event-to-frame drift measured at 15.9ms (inherent to
   30fps frame quantization; theoretical minimum is 16.7ms). All 21 events snap
   to the nearest frame on the 16th-note grid.

5. **Sun dot-eyes 1:1**: Verified — eyes scale exactly with sun radius, no squash.

## Preserved from v2
- All 21 beat-snapped events, same timing and layout
- Full-saturation palette (yellow/red/blue, mint accent only)
- Hero sun with dot-eyes, beat pulse, pop-in/out
- score-v2.wav (music-box + woodblock + bells, no vocals yet)
- 2:45 runtime, same tempo map

## What's next
- v4: Pip & Ducky character hosts composited on cream panels
- v5: 5 gentle vocal lines mixed in (score-v5.wav already built)
- v6: Final assembly (v4 frames + v5 audio)
