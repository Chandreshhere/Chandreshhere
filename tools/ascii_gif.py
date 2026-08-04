#!/usr/bin/env python3
"""
ascii_gif.py — video -> ASCII art as an animated GIF.

Why this exists alongside ascii_svg.py: an SVG stores every colour change as
its own DOM node, so full-colour ASCII costs tens of thousands of elements.
That forces a three-way trade between colour depth, framerate and whether the
page stays responsive — you can have two.

A GIF has none of that. The browser decodes it natively, so framerate is free,
colour is capped at 256 rather than by node count, and a heavy frame costs
nothing at render time. Use ascii_svg.py when you want crisp text at any zoom;
use this when you want smooth, full-colour playback.

    python3 tools/ascii_gif.py clip.mp4 -o assets/hero.gif --cols 100 --fps 14
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFont
except ImportError:
    sys.exit("Pillow is required:  python3 -m pip install pillow")

CHARSETS = {
    "blocks": " ░▒▓█",
    "classic": " .:-=+*#%@",
    "dense": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@",
    "binary": " .01",
    "dots": " ⠂⠆⠇⠏⠟⠿⡿⣿",
    "solid": "██",          # every cell filled — pure colour, no texture
}

FONTS = [
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/SFNSMono.ttf",
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for p in FONTS:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    sys.exit("no monospace font found — pass --font with a path to a .ttf")


def probe_aspect(src: Path) -> float:
    try:
        s = json.loads(run([
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,sample_aspect_ratio",
            "-of", "json", str(src),
        ]).stdout)["streams"][0]
        w, h = int(s["width"]), int(s["height"])
        sar = s.get("sample_aspect_ratio", "1:1")
        if sar and ":" in sar and "0" not in sar.split(":"):
            sn, sd = (int(x) for x in sar.split(":"))
            w = w * sn // sd
        return h / w
    except Exception:
        return 1.0


def build_lut(ramp: str, invert: bool, gamma: float) -> list[str]:
    n = len(ramp) - 1
    out = []
    for v in range(256):
        x = (v / 255.0) ** gamma
        if invert:
            x = 1.0 - x
        out.append(ramp[min(n, max(0, round(x * n)))])
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Video -> ASCII art animated GIF.")
    p.add_argument("source")
    p.add_argument("-o", "--out", default="assets/hero.gif")
    p.add_argument("--cols", type=int, default=100)
    p.add_argument("--fps", type=float, default=14)
    p.add_argument("--start", type=float)
    p.add_argument("--duration", type=float, default=5.0)
    p.add_argument("--charset", default="blocks", choices=sorted(CHARSETS))
    p.add_argument("--font-size", type=int, default=14)
    p.add_argument("--colors", type=int, default=200, help="GIF palette size, 2-256")
    p.add_argument("--contrast", type=float, default=1.3)
    p.add_argument("--gamma", type=float, default=1.0)
    p.add_argument("--saturation", type=float, default=1.35)
    p.add_argument("--invert", action="store_true")
    p.add_argument("--vivid", action="store_true",
                   help="scale each cell's colour up to full brightness. The "
                        "character glyph already carries luminance, so without "
                        "this the two multiply and everything muddies toward "
                        "the background colour")
    p.add_argument("--bg", default="#0a0a0a")
    p.add_argument("--crop-top", type=float, default=0, metavar="PCT")
    p.add_argument("--crop-bottom", type=float, default=0, metavar="PCT")
    p.add_argument("--crop-left", type=float, default=0, metavar="PCT")
    p.add_argument("--crop-right", type=float, default=0, metavar="PCT")
    p.add_argument("--boomerang", action="store_true")
    a = p.parse_args()

    if not 2 <= a.colors <= 256:
        sys.exit(f"--colors must be 2-256, got {a.colors}")
    for n, v in (("top", a.crop_top), ("bottom", a.crop_bottom),
                 ("left", a.crop_left), ("right", a.crop_right)):
        if not 0 <= v < 100:
            sys.exit(f"--crop-{n} must be 0-100, got {v}")

    for t in ("ffmpeg", "ffprobe"):
        if not shutil.which(t):
            sys.exit(f"{t} not found — brew install ffmpeg")
    src = Path(a.source).expanduser()
    if not src.exists():
        sys.exit(f"no such file: {src}")

    font = load_font(a.font_size)
    cell_w = round(font.getlength("M"))
    cell_h = round(a.font_size * 1.18)

    keep_h = (100 - a.crop_top - a.crop_bottom) / 100
    keep_w = (100 - a.crop_left - a.crop_right) / 100
    aspect = probe_aspect(src) * keep_h / keep_w
    rows = max(4, round(a.cols * aspect * cell_w / cell_h))

    tmp = Path(tempfile.mkdtemp(prefix="asciigif-"))
    try:
        crop = ""
        if any((a.crop_top, a.crop_bottom, a.crop_left, a.crop_right)):
            crop = (f"crop=iw*{keep_w:.6f}:ih*{keep_h:.6f}:"
                    f"iw*{a.crop_left / 100:.6f}:ih*{a.crop_top / 100:.6f},")

        cmd = ["ffmpeg", "-v", "error", "-y"]
        if a.start:
            cmd += ["-ss", str(a.start)]
        if a.duration:
            cmd += ["-t", str(a.duration)]
        cmd += ["-i", str(src), "-vf",
                f"fps={a.fps},{crop}scale={a.cols}:{rows}:flags=area,format=rgb24",
                str(tmp / "f%05d.png")]
        run(cmd)

        paths = sorted(tmp.glob("f*.png"))
        if not paths:
            sys.exit("ffmpeg produced no frames — check --start/--duration")

        lut = build_lut(CHARSETS[a.charset], a.invert, a.gamma)
        W, H = a.cols * cell_w, rows * cell_h
        # Only a literal space is skippable. A ramp like "solid" starts with a
        # filled glyph, and treating that as blank would skip every cell.
        ramp0 = CHARSETS[a.charset][0]
        blank = ramp0 if ramp0 == " " else None

        frames = []
        for path in paths:
            rgb = Image.open(path).convert("RGB")
            if a.saturation != 1.0:
                rgb = ImageEnhance.Color(rgb).enhance(a.saturation)
            lum = rgb.convert("L")
            if a.contrast != 1.0:
                lum = ImageEnhance.Contrast(lum).enhance(a.contrast)
            lp, cp = lum.load(), rgb.load()

            canvas = Image.new("RGB", (W, H), a.bg)
            d = ImageDraw.Draw(canvas)
            for y in range(rows):
                # Batch consecutive same-colour cells into one draw call.
                # Per-character drawing is ~8x slower for identical output.
                x = 0
                while x < a.cols:
                    ch = lut[lp[x, y]]
                    if ch == blank:
                        x += 1
                        continue
                    raw = cp[x, y]          # batch on the source colour...
                    col = raw
                    if a.vivid:
                        m = max(col)
                        if m:
                            col = tuple(min(255, c * 255 // m) for c in col)
                    buf = [ch]
                    k = x + 1
                    while k < a.cols and cp[k, y] == raw and lut[lp[k, y]] != blank:
                        buf.append(lut[lp[k, y]])
                        k += 1
                    # ...but paint with the adjusted one.
                    d.text((x * cell_w, y * cell_h), "".join(buf), font=font, fill=col)
                    x = k
            frames.append(canvas)

        if a.boomerang and len(frames) > 2:
            frames += frames[-2:0:-1]

        # One palette for the whole animation. A per-frame palette is sharper
        # in isolation but shifts between frames, and the whole image crawls.
        sample = Image.new("RGB", (W, H * min(4, len(frames))))
        for i, f in enumerate(frames[:4]):
            sample.paste(f, (0, i * H))
        pal = sample.quantize(colors=a.colors, method=Image.Quantize.FASTOCTREE)
        quantised = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]

        out = Path(a.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        quantised[0].save(out, save_all=True, append_images=quantised[1:],
                          duration=round(1000 / a.fps), loop=0, optimize=True)

        mb = out.stat().st_size / 1024 / 1024
        print(f"wrote {out}  ({W}x{H}px, {a.cols}x{rows} chars, "
              f"{len(frames)} frames, {a.colors} colours, {mb:.2f} MB)")
        if mb > 9:
            print("  ! near GitHub's proxy limit — lower --colors, --fps or --cols")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
