# neurovizr-decoded

Theme teardown instrument for NeuroVIZR sessions: measure what a journey
actually contains — binaural beat frequencies per ear, isochronic pulse rate,
light flicker rate, colour timeline, and how tightly light and sound lock
together — then render it as a self-contained dashboard.

Pure Python stdlib + ffmpeg. No installs, no dependencies.

## Use

Double-click **NeuroVIZR Decoder.command** on the Desktop, or:

```
python3 decoder.py
```

Menu option 1 rebuilds the synthesized demo end-to-end. Option 2 decodes a
real capture: session audio (wav/mp3/m4a — a screen-recording's audio works)
plus optional video of the light show.

Direct pipeline:

```
python3 analyzer.py session.wav lightshow.mov "Theme name"
python3 build_dashboard.py themes/theme-name.json
```

## Capturing a real session

- **Audio**: record the device/app output; any format ffmpeg reads.
- **Light**: film the light show. 60 fps resolves flicker to 30 Hz only —
  use 240 fps slo-mo to see gamma-rate light.

## Files

- `analyzer.py` — FFT decode (carriers per ear → binaural beat; envelope →
  isochronic pulse; frame luminance → flicker), segmentation, lock score.
- `synth_demo.py` — "First Flight (demo)": 6-minute synthesized journey,
  alpha → theta → gamma → alpha, coupled light. Demo-labelled everywhere.
- `build_dashboard.py` — theme JSON → `docs/index.html` (self-contained).
- `decoder.py` — numbered-menu CLI.

Series palette is CVD-validated for both dark and light themes.
