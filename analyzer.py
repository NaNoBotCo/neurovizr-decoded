#!/usr/bin/env python3
"""
analyzer.py — decode what a NeuroVIZR theme actually contains.

Pure stdlib + ffmpeg. No numpy, no installs, runs forever.

Audio path:  session audio  → per-channel carrier tracking → binaural beat Hz
                            → envelope FFT → isochronic (AM) modulation Hz
                            → log-band spectrogram + loudness
Light path:  video (or luminance JSON) → per-frame mean colour
                            → flicker Hz over time, luminance, hue timeline

Output: one theme JSON the dashboard renders.
"""

import json
import math
import struct
import subprocess
import sys
from pathlib import Path

FFMPEG = "ffmpeg"
FFPROBE = "ffprobe"

AUDIO_SR = 2000          # analysis sample rate (Nyquist 1000 Hz — carriers live 50–900)
AUDIO_N = 4096           # FFT window (~2.05 s → 0.488 Hz bins, parabolic interp below that)
AUDIO_HOP = 2000         # 1 s hop
CARRIER_LO, CARRIER_HI = 50.0, 900.0

ENV_SR = 100             # envelope sample rate (Nyquist 50 Hz — AM up to ~45 Hz)
ENV_N = 512              # ~5.1 s → 0.195 Hz bins
ENV_HOP = 100            # 1 s hop
MOD_LO, MOD_HI = 2.0, 46.0

FLICKER_LO = 1.0         # light flicker search band; hi bound is Nyquist-dependent
SPEC_BANDS = 48          # log-spaced spectrogram bands, 40–1000 Hz


# ---------------------------------------------------------------- FFT (stdlib)

_fft_cache = {}

def _fft_tables(n):
    tab = _fft_cache.get(n)
    if tab is None:
        levels = n.bit_length() - 1
        rev = [0] * n
        for i in range(n):
            rev[i] = int(format(i, "0{}b".format(levels))[::-1], 2)
        tw = [complex(math.cos(-2 * math.pi * k / n), math.sin(-2 * math.pi * k / n))
              for k in range(n // 2)]
        tab = (rev, tw)
        _fft_cache[n] = tab
    return tab

def fft(x):
    """Iterative radix-2 FFT. len(x) must be a power of two."""
    n = len(x)
    rev, tw = _fft_tables(n)
    a = [x[rev[i]] for i in range(n)]
    size = 2
    while size <= n:
        half = size // 2
        step = n // size
        for start in range(0, n, size):
            k = 0
            for j in range(start, start + half):
                t = a[j + half] * tw[k]
                a[j + half] = a[j] - t
                a[j] = a[j] + t
                k += step
        size *= 2
    return a

_hann_cache = {}

def hann(n):
    w = _hann_cache.get(n)
    if w is None:
        w = [0.5 - 0.5 * math.cos(2 * math.pi * i / (n - 1)) for i in range(n)]
        _hann_cache[n] = w
    return w


def dominant_freq(mag, sr, n, lo, hi, floor_ratio=6.0):
    """Peak bin in [lo, hi] Hz with parabolic interpolation.
    Returns (freq, mag) or (None, 0) if the peak doesn't stand above the band median."""
    b_lo = max(1, int(lo * n / sr))
    b_hi = min(n // 2 - 2, int(hi * n / sr))
    if b_hi <= b_lo:
        return None, 0.0
    band = mag[b_lo:b_hi + 1]
    pk = max(range(len(band)), key=band.__getitem__)
    peak = band[pk]
    med = sorted(band)[len(band) // 2]
    if med > 0 and peak / med < floor_ratio:
        return None, 0.0
    i = b_lo + pk
    ym, y0, yp = mag[i - 1], mag[i], mag[i + 1]
    denom = (ym - 2 * y0 + yp)
    delta = 0.5 * (ym - yp) / denom if denom != 0 else 0.0
    delta = max(-0.5, min(0.5, delta))
    return (i + delta) * sr / n, peak


# ---------------------------------------------------------------- audio decode

def decode_audio(path):
    """ffmpeg → interleaved stereo f32 @ AUDIO_SR."""
    cmd = [FFMPEG, "-v", "error", "-i", str(path),
           "-ac", "2", "-ar", str(AUDIO_SR), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = len(raw) // 8  # stereo frames
    flat = struct.unpack("<%df" % (n * 2), raw[:n * 8])
    return flat[0::2], flat[1::2]


def analyze_audio(path, progress=None):
    L, R = decode_audio(path)
    n_frames = len(L)
    dur = n_frames / AUDIO_SR
    win = hann(AUDIO_N)

    band_edges = [40.0 * (1000.0 / 40.0) ** (i / SPEC_BANDS) for i in range(SPEC_BANDS + 1)]
    band_bins = [(max(1, int(band_edges[i] * AUDIO_N / AUDIO_SR)),
                  max(2, int(band_edges[i + 1] * AUDIO_N / AUDIO_SR)))
                 for i in range(SPEC_BANDS)]

    t_axis, beat, f_l, f_r, rms_series, spec = [], [], [], [], [], []
    pos = 0
    total = max(1, (n_frames - AUDIO_N) // AUDIO_HOP + 1)
    step_i = 0
    while pos + AUDIO_N <= n_frames:
        segs = []
        mono_mag = None
        for ch in (L, R):
            seg = [ch[pos + i] * win[i] for i in range(AUDIO_N)]
            sp = fft([complex(v, 0.0) for v in seg])
            mag = [abs(sp[i]) for i in range(AUDIO_N // 2)]
            segs.append(mag)
            mono_mag = mag if mono_mag is None else [a + b for a, b in zip(mono_mag, mag)]
        fl, ml = dominant_freq(segs[0], AUDIO_SR, AUDIO_N, CARRIER_LO, CARRIER_HI)
        fr, mr = dominant_freq(segs[1], AUDIO_SR, AUDIO_N, CARRIER_LO, CARRIER_HI)
        t_axis.append(round(pos / AUDIO_SR + AUDIO_N / AUDIO_SR / 2, 2))
        f_l.append(round(fl, 2) if fl else None)
        f_r.append(round(fr, 2) if fr else None)
        # binaural beat: both carriers present, offset enough to matter (same-carrier
        # mono reads as < 0.8 Hz) and close enough to interfere (< 45 Hz)
        if fl and fr and 0.8 < abs(fl - fr) < 45.0:
            beat.append(round(abs(fl - fr), 2))
        else:
            beat.append(None)
        acc = 0.0
        for i in range(AUDIO_N):
            v = (L[pos + i] + R[pos + i]) * 0.5
            acc += v * v
        rms_series.append(round(math.sqrt(acc / AUDIO_N), 5))
        spec.append([round(sum(mono_mag[a:b]) / max(1, b - a), 3) for a, b in band_bins])
        pos += AUDIO_HOP
        step_i += 1
        if progress and step_i % 30 == 0:
            progress("audio %d/%d windows" % (step_i, total))

    # ---- envelope → isochronic / AM detection
    blk = AUDIO_SR // ENV_SR
    env = []
    for i in range(0, n_frames - blk, blk):
        s = 0.0
        for j in range(i, i + blk):
            s += abs(L[j]) + abs(R[j])
        env.append(s / (2 * blk))
    ewin = hann(ENV_N)
    mod_t, mod_hz, mod_depth = [], [], []
    pos = 0
    while pos + ENV_N <= len(env):
        seg = env[pos:pos + ENV_N]
        mean = sum(seg) / ENV_N
        sp = fft([complex((seg[i] - mean) * ewin[i], 0.0) for i in range(ENV_N)])
        mag = [abs(sp[i]) for i in range(ENV_N // 2)]
        f, m = dominant_freq(mag, ENV_SR, ENV_N, MOD_LO, MOD_HI, floor_ratio=8.0)
        depth = m / (mean * ENV_N / 4) if mean > 1e-6 else 0.0
        mod_t.append(round(pos / ENV_SR + ENV_N / ENV_SR / 2, 2))
        if f and depth > 0.08:
            mod_hz.append(round(f, 2))
            mod_depth.append(round(min(1.0, depth), 3))
        else:
            mod_hz.append(None)
            mod_depth.append(0.0)
        pos += ENV_HOP

    return {
        "duration_s": round(dur, 1),
        "t": t_axis, "beat": beat, "f_left": f_l, "f_right": f_r,
        "rms": rms_series,
        "mod_t": mod_t, "mod_hz": mod_hz, "mod_depth": mod_depth,
        "spec_band_edges": [round(e, 1) for e in band_edges],
        "spec": spec,
    }


# ---------------------------------------------------------------- light decode

def decode_video(path):
    """ffmpeg scale=1:1 → per-frame mean RGB. Returns (fps, [(r,g,b), ...])."""
    probe = subprocess.run(
        [FFPROBE, "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=avg_frame_rate", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True).stdout.strip()
    num, den = probe.split("/")
    fps = float(num) / float(den or 1)
    raw = subprocess.run(
        [FFMPEG, "-v", "error", "-i", str(path),
         "-vf", "scale=1:1:flags=area", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True).stdout
    frames = [(raw[i], raw[i + 1], raw[i + 2]) for i in range(0, len(raw) - 2, 3)]
    return fps, frames


def analyze_light(source):
    """source: video file, or JSON {fps, rgb:[[r,g,b],...]} (demo path)."""
    p = Path(source)
    if p.suffix.lower() == ".json":
        data = json.loads(p.read_text())
        fps, frames = data["fps"], [tuple(f) for f in data["rgb"]]
    else:
        fps, frames = decode_video(p)

    luma = [0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b in frames]
    nyq = fps / 2.0
    n_fft = 256
    while n_fft > len(luma):
        n_fft //= 2
    win = hann(n_fft)
    hop = int(fps)  # 1 s

    t_axis, flicker, flick_depth = [], [], []
    pos = 0
    while pos + n_fft <= len(luma):
        seg = luma[pos:pos + n_fft]
        mean = sum(seg) / n_fft
        sp = fft([complex((seg[i] - mean) * win[i], 0.0) for i in range(n_fft)])
        mag = [abs(sp[i]) for i in range(n_fft // 2)]
        f, m = dominant_freq(mag, fps, n_fft, FLICKER_LO, nyq - 1.0, floor_ratio=5.0)
        t_axis.append(round(pos / fps + n_fft / fps / 2, 2))
        if f and mean > 1.0 and m / (mean * n_fft / 4) > 0.05:
            flicker.append(round(f, 2))
            flick_depth.append(round(min(1.0, m / (mean * n_fft / 4)), 3))
        else:
            flicker.append(None)
            flick_depth.append(0.0)
        pos += hop

    # per-second hue ribbon + luminance
    sec = int(fps)
    hue_hex, luma_s = [], []
    for i in range(0, len(frames) - sec + 1, sec):
        rs = sum(f[0] for f in frames[i:i + sec]) / sec
        gs = sum(f[1] for f in frames[i:i + sec]) / sec
        bs = sum(f[2] for f in frames[i:i + sec]) / sec
        hue_hex.append("#%02x%02x%02x" % (int(rs), int(gs), int(bs)))
        luma_s.append(round(sum(luma[i:i + sec]) / sec, 2))

    return {
        "fps": fps, "nyquist_hz": round(nyq, 1),
        "t": t_axis, "flicker": flicker, "flicker_depth": flick_depth,
        "hue": hue_hex, "luma": luma_s,
    }


# ---------------------------------------------------------------- synthesis

BANDS = [("delta", 0.5, 4), ("theta", 4, 8), ("alpha", 8, 13),
         ("beta", 13, 30), ("gamma", 30, 46)]

def band_of(hz):
    for name, lo, hi in BANDS:
        if lo <= hz < hi:
            return name
    return None


def segment_protocol(audio):
    """Merge the beat/AM timeline into labelled phases."""
    t = audio["t"]
    stim = []
    for i in range(len(t)):
        b = audio["beat"][i]
        m = audio["mod_hz"][i] if i < len(audio["mod_hz"]) else None
        if b is not None:
            stim.append(("binaural", b))
        elif m is not None:
            stim.append(("isochronic", m))
        else:
            stim.append((None, None))
    segs = []
    for i, (kind, hz) in enumerate(stim):
        band = band_of(hz) if hz else None
        key = (kind, band)
        if segs and segs[-1]["key"] == key:
            segs[-1]["end"] = t[i]
            segs[-1]["hz"].append(hz)
        else:
            segs.append({"key": key, "start": t[i], "end": t[i], "hz": [hz]})
    out = []
    for s in segs:
        if s["end"] - s["start"] < 8:
            continue
        kind, band = s["key"]
        hzs = [h for h in s["hz"] if h]
        out.append({
            "start": round(s["start"], 1), "end": round(s["end"], 1),
            "technique": kind or "ambient", "band": band or "—",
            # first → last, so a descending ramp reads 10→8, not 8–10
            "hz_from": round(hzs[0], 1) if hzs else None,
            "hz_to": round(hzs[-1], 1) if hzs else None,
        })
    return out


def coupling(audio, light):
    """Where sound stimulus and light flicker are both present: Pearson r + mean |Δ|.
    Harmonic-aware: a flicker at half or double the audio rate counts as coupled."""
    a_by_t = {}
    for i, tt in enumerate(audio["t"]):
        hz = audio["beat"][i]
        if hz is None and i < len(audio["mod_hz"]):
            hz = audio["mod_hz"][i]
        if hz is not None:
            a_by_t[int(tt)] = hz
    xs, ys, harm = [], [], 0
    for i, tt in enumerate(light["t"]):
        f = light["flicker"][i]
        a = a_by_t.get(int(tt))
        if f is None or a is None:
            continue
        best = min((f, f * 2, f / 2), key=lambda v: abs(v - a))
        if best != f and abs(best - a) < 1.5:
            harm += 1
        xs.append(a)
        ys.append(best)
    n = len(xs)
    if n < 8:
        return {"n": n, "r": None, "mean_abs_diff": None, "pct_locked": 0, "harmonic_locks": harm}
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    vy = math.sqrt(sum((y - my) ** 2 for y in ys))
    r = cov / (vx * vy) if vx > 0 and vy > 0 else None
    diffs = [abs(x - y) for x, y in zip(xs, ys)]
    locked = sum(1 for d in diffs if d < 1.5)
    return {
        "n": n,
        "r": round(r, 3) if r is not None else None,
        "mean_abs_diff": round(sum(diffs) / n, 2),
        "pct_locked": round(100.0 * locked / n, 1),
        "harmonic_locks": harm,
    }


def analyze_theme(audio_path, light_source, name, is_demo=False, progress=print):
    progress("decoding audio: %s" % audio_path)
    audio = analyze_audio(audio_path, progress=progress)
    progress("decoding light: %s" % light_source)
    light = analyze_light(light_source) if light_source else None
    theme = {
        "name": name,
        "is_demo": is_demo,
        "audio": audio,
        "light": light,
        "segments": segment_protocol(audio),
        "coupling": coupling(audio, light) if light else None,
    }
    return theme


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: analyzer.py <audio> <video-or-luma-json|-> [name] [--demo]")
        sys.exit(1)
    audio_p = sys.argv[1]
    light_p = None if sys.argv[2] == "-" else sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else Path(audio_p).stem
    theme = analyze_theme(audio_p, light_p, name, is_demo="--demo" in sys.argv)
    out = Path(__file__).parent / "themes" / (name.lower().replace(" ", "-") + ".json")
    out.write_text(json.dumps(theme))
    print("wrote", out)
