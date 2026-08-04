#!/usr/bin/env python3
"""
pixelate.py — turn a video / GIF into a looping pixel-art GIF banner.

Animated GIFs render and loop in a GitHub README, so this is the other half of
the aesthetic: a crunchy, palette-limited, nearest-neighbour-upscaled clip that
reads as sprite art instead of compressed video.

    python3 tools/pixelate.py clip.mp4 -o assets/banner.gif --pixels 220 --colors 32

Keep it under ~10 MB or GitHub's image proxy will drop it; the script warns.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# name -> ffmpeg colour grade applied before quantising
GRADES = {
    "none": None,
    "gameboy": "colorchannelmixer=.35:.65:.05:0:.25:.75:.05:0:.15:.45:.05:0",
    "crt": "eq=contrast=1.25:saturation=1.35:gamma=0.95",
    "washed": "eq=contrast=1.1:saturation=0.55:brightness=0.03",
    "neon": "eq=contrast=1.3:saturation=1.8,hue=h=8",
    "noir": "hue=s=0,eq=contrast=1.45",
}


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def main() -> int:
    p = argparse.ArgumentParser(description="Video/GIF -> pixel-art GIF banner.")
    p.add_argument("source")
    p.add_argument("-o", "--out", default="assets/banner.gif")
    p.add_argument("--pixels", type=int, default=220,
                   help="internal width in 'pixels' before upscaling — lower is chunkier")
    p.add_argument("--width", type=int, default=880, help="final output width")
    p.add_argument("--colors", type=int, default=32, help="palette size, 2-256")
    p.add_argument("--fps", type=float, default=12)
    p.add_argument("--start", type=float)
    p.add_argument("--duration", type=float, default=5.0)
    p.add_argument("--grade", default="crt", choices=sorted(GRADES))
    p.add_argument("--dither", default="bayer",
                   choices=["bayer", "floyd_steinberg", "sierra2_4a", "none"])
    p.add_argument("--bayer-scale", type=int, default=4,
                   help="0-5; higher = coarser, more retro dither pattern")
    p.add_argument("--boomerang", action="store_true",
                   help="play forward then reverse so the loop never cuts")
    p.add_argument("--crop-top", type=float, default=0, metavar="PCT",
                   help="chop this %% off the top — use it to cut burnt-in "
                        "titles or captions out of the frame")
    p.add_argument("--crop-bottom", type=float, default=0, metavar="PCT")
    p.add_argument("--crop-left", type=float, default=0, metavar="PCT")
    p.add_argument("--crop-right", type=float, default=0, metavar="PCT")
    p.add_argument("--square", action="store_true",
                   help="centre-crop to 1:1, which is the shape the README's "
                        "About slot expects")
    a = p.parse_args()

    for name, v in (("--crop-top", a.crop_top), ("--crop-bottom", a.crop_bottom),
                    ("--crop-left", a.crop_left), ("--crop-right", a.crop_right)):
        if not 0 <= v < 100:
            sys.exit(f"{name} must be between 0 and 100, got {v}")
    if a.crop_top + a.crop_bottom >= 100 or a.crop_left + a.crop_right >= 100:
        sys.exit("crop percentages leave nothing of the frame")

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found — brew install ffmpeg")
    src = Path(a.source).expanduser()
    if not src.exists():
        sys.exit(f"no such file: {src}")

    grade = GRADES[a.grade]
    chain = [f"fps={a.fps}"]

    # Crop first, before anything else touches the frame — cropping after the
    # downscale would just throw away pixels we already paid to compute.
    if any((a.crop_top, a.crop_bottom, a.crop_left, a.crop_right)):
        w = f"iw*{(100 - a.crop_left - a.crop_right) / 100:.6f}"
        h = f"ih*{(100 - a.crop_top - a.crop_bottom) / 100:.6f}"
        chain.append(f"crop={w}:{h}:iw*{a.crop_left / 100:.6f}:ih*{a.crop_top / 100:.6f}")
    if a.square:
        chain.append("crop='min(iw,ih)':'min(iw,ih)'")

    if grade:
        chain.append(grade)
    # Down to a tiny buffer with area averaging, then back up with nearest
    # neighbour — that second step is what makes the pixels hard-edged.
    chain.append(f"scale={a.pixels}:-1:flags=area")
    if a.boomerang:
        chain.append("split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1:a=0")
    chain.append(f"scale={a.width}:-1:flags=neighbor")
    vf = ",".join(chain)

    dither = (f"bayer:bayer_scale={a.bayer_scale}"
              if a.dither == "bayer" else a.dither)

    tmp = Path(tempfile.mkdtemp(prefix="pixelate-"))
    palette = tmp / "palette.png"
    try:
        head = ["ffmpeg", "-v", "error", "-y"]
        if a.start:
            head += ["-ss", str(a.start)]
        if a.duration:
            head += ["-t", str(a.duration)]
        head += ["-i", str(src)]

        # Pass 1: a single palette for the whole clip, so colours don't crawl.
        run(head + ["-vf", f"{vf},palettegen=max_colors={a.colors}:stats_mode=diff",
                    str(palette)])

        out = Path(a.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        run(head + ["-i", str(palette), "-lavfi",
                    f"{vf}[x];[x][1:v]paletteuse=dither={dither}:diff_mode=rectangle",
                    "-loop", "0", str(out)])

        mb = out.stat().st_size / 1024 / 1024
        print(f"wrote {out}  ({a.width}px wide, {a.colors} colours, {mb:.2f} MB)")
        if mb > 9:
            print("  ! close to GitHub's proxy limit — lower --colors, --fps or --duration.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
