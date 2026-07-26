#!/usr/bin/env python3
"""NeuroVIZR Decoder — numbered menu. Big text, one keypress per step."""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
PY = sys.executable or "python3"


def run(*args):
    subprocess.run([PY] + [str(a) for a in args], cwd=HERE)


def newest_theme():
    themes = sorted((HERE / "themes").glob("*.json"), key=lambda p: p.stat().st_mtime)
    return themes[-1] if themes else None


def menu():
    while True:
        print()
        print("=" * 46)
        print("   NEUROVIZR DECODER")
        print("=" * 46)
        print()
        print("  1. Decode the DEMO journey (start fresh)")
        print("  2. Decode a REAL session capture")
        print("  3. Rebuild dashboard from latest decode")
        print("  4. Open the dashboard")
        print("  0. Quit")
        print()
        choice = input("  Pick a number: ").strip()

        if choice == "1":
            print("\n  Synthesizing demo session…")
            run(HERE / "synth_demo.py")
            print("  Decoding (about 10 seconds)…")
            run(HERE / "analyzer.py", HERE / "media" / "demo-first-flight.wav",
                HERE / "media" / "demo-first-flight-light.json", "First Flight demo", "--demo")
            run(HERE / "build_dashboard.py")
            print("\n  Done. Pick 4 to open it.")

        elif choice == "2":
            print()
            audio = input("  Path to session AUDIO (drag the file here): ").strip().strip("'\"")
            if not audio or not Path(audio).exists():
                print("  That file isn't there — check the path and try again.")
                continue
            video = input("  Path to light-show VIDEO (Enter to skip): ").strip().strip("'\"")
            if video and not Path(video).exists():
                print("  That video isn't there — skipping light analysis.")
                video = ""
            name = input("  Theme name: ").strip() or Path(audio).stem
            print("\n  Decoding — a few minutes for a full-length session…")
            run(HERE / "analyzer.py", audio, video or "-", name)
            slug = name.lower().replace(" ", "-") + ".json"
            run(HERE / "build_dashboard.py", HERE / "themes" / slug)
            print("\n  Done. Pick 4 to open it.")

        elif choice == "3":
            t = newest_theme()
            if t:
                run(HERE / "build_dashboard.py", t)
            else:
                print("  Nothing decoded yet — pick 1 first.")

        elif choice == "4":
            subprocess.run(["open", str(HERE / "docs" / "index.html")])

        elif choice == "0":
            print("  Until next time.")
            return

        else:
            print("  Just the numbers on the list, please.")


if __name__ == "__main__":
    try:
        menu()
    except (KeyboardInterrupt, EOFError):
        print()
