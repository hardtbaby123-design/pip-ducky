#!/usr/bin/env python3
"""Synthesize the 'Hello, Sun!' music-box score.
C major, 92 BPM base, evolving arrangement across 5 scenes + intro.
Grok co-owner spec: instrumental music-box only, NO lazy looping —
layers evolve per scene; slight ritardando in the finale.
Outputs: build/score.wav (44.1kHz mono->stereo) and prints scene boundary times as JSON.
"""
import json
import numpy as np

SR = 44100
BPM = 92.0
BEAT = 60.0 / BPM          # 0.65217s
BAR = BEAT * 4             # 2.6087s
N_BARS = 62

# --- tempo map with ritardando over bars 58..62 ---
beat_t = []   # start time of every beat
t = 0.0
for bar in range(N_BARS):
    if bar < 58:
        bd = BEAT
    else:
        # ramp beat duration 1.0x -> 1.25x across bars 58..61
        f = (bar - 58) / 4.0
        bd = BEAT * (1.0 + 0.25 * f)
    for _ in range(4):
        beat_t.append(t)
        t += bd
END_T = t + 3.0  # room for final swell + fade
print(f"total music time ~ {t:.2f}s, END_T={END_T:.2f}s")

FREQ = {
    'C3': 130.81, 'F2': 87.31, 'G2': 98.00, 'A2': 110.00,
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
    'G4': 392.00, 'A4': 440.00, 'B4': 493.88, 'C5': 523.25,
    'E5': 659.25, 'G5': 783.99,
}
CHORDS = {  # line -> (name, root bass, pad tones)
    'L1': ('C',  'C3', ['C4', 'E4', 'G4']),
    'L2': ('G',  'G2', ['G3', 'B3', 'D4']),
    'L3': ('Am', 'A2', ['A3', 'C4', 'E4']),
    'L4': ('F',  'F2', ['F3', 'A3', 'C4']),
}
FREQ.update({'G3': 196.00, 'B3': 246.94, 'D4b': 293.66, 'A3': 220.00, 'F3': 174.61})
# fix pad tone names
CHORDS['L2'] = ('G', 'G2', ['G3', 'B3', 'D4'])
MELODY = {
    'L1': ['G4', 'A4', 'B4', 'C5', 'B4', 'A4', 'G4'],
    'L2': ['E4', 'F4', 'G4', 'A4', 'G4', 'F4', 'E4'],
    'L3': ['E4', 'F4', 'G4', 'A4', 'G4', 'F4', 'E4'],
    'L4': ['G4', 'F4', 'E4', 'D4', 'C4'],
}

def musicbox(freq, start, dur, gain=0.5, bright=1.0, sr=SR):
    n = int(dur * sr)
    if n <= 0:
        return np.zeros(0), 0
    tt = np.arange(n) / sr
    env = np.exp(-tt / 0.9)
    # gentle attack to avoid clicks
    a = min(int(0.005 * sr), n)
    env[:a] *= np.linspace(0, 1, a)
    sig = (np.sin(2 * np.pi * freq * tt)
           + 0.32 * bright * np.sin(2 * np.pi * 2 * freq * tt)
           + 0.10 * bright * np.sin(2 * np.pi * 3 * freq * tt))
    return gain * env * sig, start

def bass(freq, start, dur, gain=0.30, sr=SR):
    n = int(dur * sr)
    tt = np.arange(n) / sr
    env = np.minimum(1, tt / 0.08) * np.exp(-tt / 1.6)
    return gain * env * np.sin(2 * np.pi * freq * tt), start

def pad(freqs, start, dur, gain=0.10, sr=SR):
    n = int(dur * sr)
    tt = np.arange(n) / sr
    atk = np.minimum(1, tt / 0.8)
    rel = np.minimum(1, (dur - tt) / 0.8 + 1e-9)
    env = np.clip(np.minimum(atk, rel), 0, 1)
    sig = sum(np.sin(2 * np.pi * f * tt) for f in freqs) / len(freqs)
    return gain * env * sig, start

def shaker(start, gain=0.06, sr=SR):
    n = int(0.07 * sr)
    tt = np.arange(n) / sr
    env = np.exp(-tt / 0.02)
    noise = np.random.default_rng(int(start * 1000) + 7).standard_normal(n)
    # crude highpass: diff
    hp = np.diff(noise, prepend=noise[0])
    return gain * env * hp, start

def place(buf, sig, start, sr=SR):
    i = int(start * sr)
    j = i + len(sig)
    if i >= len(buf):
        return
    buf[i:min(j, len(buf))] += sig[:max(0, min(j, len(buf)) - i)]

buf = np.zeros(int(END_T * SR))

def bar_start(b):
    return beat_t[b * 4]

def play_line(line, bar, gain=0.5, bass_on=True, shaker_on=False, shaker_gain=0.06,
              pad_on=False, octave_up=False, bright=1.0):
    notes = MELODY[line]
    _, root, pads = CHORDS[line]
    b0 = bar * 4
    for i, nn in enumerate(notes):
        st = beat_t[b0 + i]
        s, _ = musicbox(FREQ[nn], st, 1.6, gain=gain, bright=bright)
        place(buf, s, st)
        if octave_up:
            s2, _ = musicbox(FREQ[nn] * 2, st, 1.2, gain=gain * 0.45, bright=1.4)
            place(buf, s2, st)
    if bass_on:
        s, _ = bass(FREQ[root], beat_t[b0], BEAT * 7, gain=0.30)
        place(buf, s, beat_t[b0])
    if pad_on:
        s, _ = pad([FREQ[p] for p in pads], beat_t[b0], BEAT * 8, gain=0.10)
        place(buf, s, beat_t[b0])
    if shaker_on:
        for b in range(8):
            if b % 4 == 1 or b % 4 == 2 or b % 4 == 3:  # skip downbeat
                st = beat_t[b0 + b] + BEAT / 2
                s, _ = shaker(st, gain=shaker_gain)
                place(buf, s, st)

def chorus(bar, **kw):
    for i, L in enumerate(['L1', 'L2', 'L3', 'L4']):
        play_line(L, bar + i * 2, **kw)

# ---- arrangement ----
# intro bars 0-4: simplified melody, music-box only
play_line('L1', 0, gain=0.42, bass_on=False)
play_line('L2', 2, gain=0.42, bass_on=False)
# S1 bars 4-12
chorus(4, gain=0.5, bass_on=True)
# S2 bars 12-20
chorus(12, gain=0.5, bass_on=True, shaker_on=True, shaker_gain=0.05)
# S3 bars 20-32 (peak): 1.5 choruses
chorus(20, gain=0.52, bass_on=True, shaker_on=True, shaker_gain=0.09, pad_on=True)
play_line('L1', 28, gain=0.52, bass_on=True, shaker_on=True, shaker_gain=0.09, pad_on=True)
play_line('L2', 30, gain=0.52, bass_on=True, shaker_on=True, shaker_gain=0.09, pad_on=True)
# S4 bars 32-44 (reset): no bass/pad, soft shaker
chorus(32, gain=0.46, bass_on=False, shaker_on=True, shaker_gain=0.05)
play_line('L1', 40, gain=0.46, bass_on=False, shaker_on=True, shaker_gain=0.05)
play_line('L2', 42, gain=0.46, bass_on=False, shaker_on=True, shaker_gain=0.05)
# S5 bars 44-62 (finale): full + octave doubling, ritard in 58-62
chorus(44, gain=0.52, bass_on=True, shaker_on=True, shaker_gain=0.08, pad_on=True, octave_up=True)
play_line('L1', 52, gain=0.52, bass_on=True, shaker_on=True, shaker_gain=0.08, pad_on=True, octave_up=True)
play_line('L2', 54, gain=0.52, bass_on=True, shaker_on=True, shaker_gain=0.08, pad_on=True, octave_up=True)
play_line('L3', 56, gain=0.52, bass_on=True, shaker_on=True, shaker_gain=0.08, pad_on=True, octave_up=True)
# final stretched "good morning": whole notes over bars 58-62
b0 = 58 * 4
LAST_BD = BEAT * 1.25  # final ritard beat duration, for extrapolation past the map
def beat_time(idx):
    if idx < len(beat_t):
        return beat_t[idx]
    return beat_t[-1] + (idx - (len(beat_t) - 1)) * LAST_BD
for i, nn in enumerate(['G4', 'F4', 'E4', 'D4', 'C4']):
    st = beat_time(b0 + i * 4)
    dur = beat_time(b0 + (i + 1) * 4) - st
    s, _ = musicbox(FREQ[nn], st, dur, gain=0.5, bright=1.2)
    place(buf, s, st)
    s2, _ = musicbox(FREQ[nn] * 2, st, dur * 0.8, gain=0.22, bright=1.4)
    place(buf, s2, st)
# tonic swell to close (builds under the final two whole notes)
swell_t = beat_time(58 * 4 + 8)
s, _ = pad([FREQ[p] for p in ['C4', 'E4', 'G4', 'C5']], swell_t, 8.0, gain=0.16)
place(buf, s, swell_t)

# ---- master: fades + normalize + soft limit ----
n = len(buf)
fi = int(1.0 * SR)
buf[:fi] *= np.linspace(0, 1, fi)
fo = int(3.0 * SR)
buf[-fo:] *= np.linspace(1, 0, fo)
peak = np.max(np.abs(buf))
buf = buf / peak * 0.89
buf = np.tanh(buf * 1.1) * 0.95  # gentle glue

stereo = np.stack([buf, buf], axis=1)
import wave
with wave.open('build/score.wav', 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(stereo, -1, 1) * 32767).astype(np.int16).tobytes())

bounds = {
    'intro_end': round(bar_start(4), 3),
    's1_end': round(bar_start(12), 3),
    's2_end': round(bar_start(20), 3),
    's3_end': round(bar_start(32), 3),
    's4_end': round(bar_start(44), 3),
    'end': round(END_T, 3),
}
print(json.dumps(bounds))
with open('build/boundaries.json', 'w') as f:
    json.dump(bounds, f, indent=2)
print("wrote build/score.wav")
