#!/usr/bin/env python3
"""
synth_demo.py — synthesize a demo journey so the decoder has something to decode.

"First Flight (demo)" — 6 minutes, 4 phases, the shape a real NeuroVIZR-style
session takes. Clearly labelled demo everywhere it surfaces. Swap in a real
session capture and none of this file matters anymore.

Phases:
  Arrival   0–90s    binaural alpha 10 Hz  (carriers 200/210)   amber light, 10 Hz
  Descent   90–210s  beat ramps 10 → 5 Hz (alpha → theta)       violet light, follows
  Ignition  210–270s isochronic gamma 40 Hz (AM, no binaural)   blue light, 20 Hz (half-harmonic)
  Return    270–360s binaural alpha 10 Hz, fade out             green light, 10 Hz
"""

import json
import math
import struct
import wave
from pathlib import Path

SR = 8000
DUR = 360
FPS = 60.0

HERE = Path(__file__).parent
MEDIA = HERE / "media"


def phase_at(t):
    if t < 90:
        return "arrival"
    if t < 210:
        return "descent"
    if t < 270:
        return "ignition"
    return "return"


def beat_hz(t):
    if t < 90:
        return 10.0
    if t < 210:
        return 10.0 - 5.0 * (t - 90) / 120.0   # 10 → 5
    if t < 270:
        return None                             # isochronic phase
    return 10.0


def carrier_hz(t):
    if t < 90:
        return 200.0
    if t < 210:
        return 200.0 - 30.0 * (t - 90) / 120.0  # 200 → 170
    if t < 270:
        return 180.0
    return 200.0


def amp_env(t):
    a = min(1.0, t / 6.0)                       # 6 s fade in
    if t > DUR - 20:
        a *= max(0.0, (DUR - t) / 20.0)         # 20 s fade out
    return 0.55 * a


def synth_audio():
    frames = bytearray()
    ph_l = ph_r = ph_pad = 0.0
    two_pi = 2 * math.pi
    for i in range(SR * DUR):
        t = i / SR
        c = carrier_hz(t)
        b = beat_hz(t)
        a = amp_env(t)
        if b is not None:
            ph_l += two_pi * c / SR
            ph_r += two_pi * (c + b) / SR
            sl = math.sin(ph_l) * a
            srt = math.sin(ph_r) * a
        else:
            # isochronic: same carrier both ears, 40 Hz amplitude gate
            ph_l += two_pi * c / SR
            gate = 0.5 + 0.5 * math.sin(two_pi * 40.0 * t - math.pi / 2)
            s = math.sin(ph_l) * a * gate
            sl = srt = s
        # soft low pad for warmth (below the 50 Hz carrier-search floor)
        ph_pad += two_pi * 38.0 / SR
        pad = math.sin(ph_pad) * 0.06 * a
        sl += pad
        srt += pad
        frames += struct.pack("<hh", int(max(-1, min(1, sl)) * 32000),
                              int(max(-1, min(1, srt)) * 32000))
    out = MEDIA / "demo-first-flight.wav"
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(bytes(frames))
    return out


PHASE_COLOR = {
    "arrival": (255, 170, 80),    # amber
    "descent": (140, 80, 220),    # violet
    "ignition": (90, 160, 255),   # electric blue
    "return": (80, 220, 160),     # green
}

def light_flicker_hz(t):
    b = beat_hz(t)
    if b is not None:
        return b
    return 20.0   # ignition: 20 Hz — half-harmonic of the 40 Hz audio gate


def synth_light():
    n = int(FPS * DUR)
    rgb = []
    fph = 0.0  # integrated flicker phase — sin(2π·hz(t)·t) would chirp during ramps
    for i in range(n):
        t = i / FPS
        ph = phase_at(t)
        r0, g0, b0 = PHASE_COLOR[ph]
        # crossfade colours over 8 s at phase joins
        for edge in (90, 210, 270):
            if 0 <= t - edge < 8:
                prev = PHASE_COLOR[phase_at(edge - 1)]
                f = (t - edge) / 8.0
                r0 = prev[0] + (r0 - prev[0]) * f
                g0 = prev[1] + (g0 - prev[1]) * f
                b0 = prev[2] + (b0 - prev[2]) * f
        hz = light_flicker_hz(t)
        fph += 2 * math.pi * hz / FPS
        base = 0.55 + 0.10 * math.sin(2 * math.pi * t / 37.0)   # slow breathing
        depth = 0.38
        flick = base + depth * math.sin(fph)
        flick *= amp_env(t) / 0.55
        flick = max(0.0, min(1.0, flick))
        rgb.append([int(r0 * flick), int(g0 * flick), int(b0 * flick)])
    out = MEDIA / "demo-first-flight-light.json"
    out.write_text(json.dumps({"fps": FPS, "rgb": rgb}))
    return out


if __name__ == "__main__":
    MEDIA.mkdir(exist_ok=True)
    wav = synth_audio()
    print("wrote", wav)
    lj = synth_light()
    print("wrote", lj)
