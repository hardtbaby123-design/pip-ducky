# Video #1 "Hello, Sun!" — Production Spec (v1 FINAL)

**File out:** `build/hello-sun-v1.mp4` — 1920×1080, 30fps, H.264 + AAC 192k, 165.7s (2:45).
**Audio:** `build/score.wav` — original instrumental music-box score, C major, 92 BPM base.
**Build scripts:** `build/01-synth-audio.py` (score synthesis) + `build/02-assemble-video.py` (ffmpeg assembly). Reproducible end-to-end.

---

## Scene map (cuts on musical phrase boundaries)

| Seg | Time | Visual | Motion | Audio arrangement |
|-----|------|--------|--------|-------------------|
| Intro | 0:00–0:10 | Title card "HELLO, SUN!" | Slow push-in | Music-box, simplified melody (lines 1–2 only) |
| S1 | 0:10–0:31 | Yellow circles, black bg | Slow pull-out | Full chorus + soft bass roots |
| S2 | 0:31–0:52 | Mint triangles, white bg | Slow push-in | Chorus + bass + soft shaker |
| S3 | 0:52–1:23 | Full ensemble, black bg | Slow pull-out | **Peak:** chorus ×1.5 + bass + full shaker + warm pad |
| S4 | 1:23–1:55 | Pink rects + blue diamonds, white bg | Slow push-in | **Reset:** chorus ×1.5, music-box + soft shaker (no bass/pad) |
| S5 | 1:55–2:45 | Title card resolve | Very slow pull-out | Full + octave-up doubling; final "good morning" stretched over 4 bars with ritardando; tonic swell close |

Transitions: 0.8s crossfades centered on each boundary. 0.6s fade-in from black; 2s fade-out to black.

## Audio arrangement detail

- **Melody** (original, owned IP): L1 "Hello sun" G4→C5→G4 · L2 "Shine on me" E4→A4→E4 · L3 "Hello birds, hello flowers" E4→A4 (mirror of L1, third lower) · L4 "Good morning" G4→C4 descending. Chords: C – G – Am – F.
- **Timbre:** music-box = sine + 0.32×2nd + 0.10×3rd harmonic, exp decay τ=0.9s.
- **Bass:** soft sine roots (C3/G2/A2/F2), scenes S1–S3, S5.
- **Shaker:** filtered noise ticks on offbeats; intensity S2 0.05 → S3 0.09 (peak) → S4 0.05 → S5 0.08.
- **Pad:** triad swells, S3 + S5 only.
- **Finale:** melody doubled one octave up (glockenspiel-bright), bars 58–62 ritardando 92→~74 BPM, final whole-note "good morning" + C-major tonic swell, 3s fade.
- **Master:** peak-normalized −1dB, tanh glue, stereo.

## Motion rules (enforced)

- One continuous slow zoom per scene (alternating push-in / pull-out). Max 10% travel per scene — never fast, never jarring.
- No whip pans, no flashes, no strobing. Black/white backgrounds alternate for contrast rhythm.
- Cuts land on phrase boundaries (= beat-aligned by construction).

## What v1 deliberately omits (future upgrades)

- Vocals (real vocalist records the chorus for v2 — never synthesized).
- AI-animated motion clips (revisit after visual system is proven).
- On-screen lyrics (sensory lane doesn't need them; add for learning lane).
- End-screen subscribe animation (add once channel has 3+ videos).

## Quality checklist (Grok's bar)

- [ ] Every cut lands on a beat (±0.4s of phrase boundary — verified in build)
- [ ] Contrast holds at 50% phone brightness (black/white fields, thick outlines)
- [ ] Zero audio drift (single continuous render, cuts derived from the tempo map)
- [ ] Thumbnail/title/video same visual family
- [ ] Full 2:45 watch-through feels "held" — no dead air (arrangement evolves every scene)
