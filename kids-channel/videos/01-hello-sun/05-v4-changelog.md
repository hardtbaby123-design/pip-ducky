# Video #1 "Hello, Sun!" — v4 Changelog (Character hosts)

**Build:** `build/08-composite-v4.py` → `build/v4_frames/` (v3 frames + characters)
**Input:** v3 picture-locked frames (no re-render)

## Grok's binding decisions implemented

1. **Strict hosts, not replacements**: Pip and Ducky appear ONLY on the lower third,
   on cream rounded panels. The abstract sensory shapes remain the sole content
   in all other moments.

2. **Five appearances** on the downbeat of events 4, 8, 12, 16, 20 (1-indexed):
   - Event 4 (suns, black): Pip wave
   - Event 8 (diamonds, white): Ducky splash
   - Event 12 (bluedense, white): Pip arms-up
   - Event 16 (finale, black): Ducky wave
   - Event 20 (drift, white): Pip point

3. **Exactly 4 beats per appearance** (78 frames): 6-frame fade in, static hold,
   6-frame fade out. No tweening between poses (Grok veto) — each appearance is
   a single static pose hold.

4. **No hero-sun occlusion**: Panel is 440x320, bottom-center, top edge at y=565.
   Hero sun face (eyes at y=396) is always clear.

5. **Cream panel design**: Rounded rectangle (r=36), cream #FDF2E2 matching sprite
   backgrounds, character scaled to ~260px tall, centered.

## Preserved from v3
- All v3 picture-locked frames unchanged underneath
- 2x supersampled rendering, 3px strokes, 2-frame crossfades
