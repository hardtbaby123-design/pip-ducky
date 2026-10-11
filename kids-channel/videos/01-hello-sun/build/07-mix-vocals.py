#!/usr/bin/env python3
"""Mix 5 gentle vocal lines into score-v2.wav -> score-v5.wav.
Grok binding: exactly 5 lines on woodblock downbeats, dry, no reverb."""
import numpy as np, wave, subprocess, os

SR = 44100
BPM = 92.0
BEAT = 60.0 / BPM
N_BARS = 62
beat_t = []
t = 0.0
for bar in range(N_BARS):
    bd = BEAT if bar < 58 else BEAT * (1.0 + 0.25 * (bar - 58) / 4.0)
    for _ in range(4):
        beat_t.append(t)
        t += bd

VOCALS = [
    ('v_hello_sun.mp3', 0),      # bar 1
    ('v_up_we_go.mp3', 32),      # bar 9
    ('v_big_bright.mp3', 64),    # bar 17
    ('v_wave_hello.mp3', 96),    # bar 25
    ('v_goodnight_sun.mp3', 128) # bar 33
]

def load_mp3(path):
    wav = '/tmp/_vocal.wav'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', path,
                    '-ar', str(SR), '-ac', '1', wav], check=True)
    with wave.open(wav, 'rb') as w:
        n = w.getnframes()
        data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    return data

def load_wav_stereo(path):
    with wave.open(path, 'rb') as w:
        n = w.getnframes()
        ch = w.getnchannels()
        data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
        return data.reshape(-1, ch)

base = load_wav_stereo('build/score-v2.wav')
print('base:', base.shape, flush=True)

for mp3, beat_idx in VOCALS:
    vocal = load_mp3(f'build/vocals/{mp3}')
    # gentle fade in/out to avoid clicks, keep it dry
    f = int(0.03 * SR)
    vocal[:f] *= np.linspace(0, 1, f)
    vocal[-f:] *= np.linspace(1, 0, f)
    # normalize to consistent gentle level (~-18 LUFS approx -> peak ~0.35)
    peak = np.max(np.abs(vocal))
    vocal = vocal / peak * 0.38
    start_t = beat_t[beat_idx]
    i0 = int(start_t * SR)
    i1 = i0 + len(vocal)
    if i1 > len(base):
        pad = np.zeros((i1 - len(base), 2))
        base = np.vstack([base, pad])
    stereo_v = np.stack([vocal, vocal], axis=1)
    base[i0:i1] += stereo_v
    print(f'placed {mp3} at t={start_t:.2f}s (bar {beat_idx//4 + 1})', flush=True)

# soft master (same glue as v2)
peak = np.max(np.abs(base))
base = base / peak * 0.89
base = np.tanh(base * 1.1) * 0.95

with wave.open('build/score-v5.wav', 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(base, -1, 1) * 32767).astype(np.int16).tobytes())
print('wrote build/score-v5.wav', flush=True)
