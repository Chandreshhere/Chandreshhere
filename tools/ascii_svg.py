#!/usr/bin/env python3
"""
ascii_svg.py — turn a video / GIF into an ASCII-art animation that plays
inside a GitHub README.

GitHub strips <script>, <video> and <style> from markdown, but it happily
renders an <img src="...svg"> whose animation lives *inside* the SVG as CSS
keyframes. So we bake every ASCII frame into one SVG and cross-fade them with
step timing. No JS, no external service, works on any repo.

    python3 tools/ascii_svg.py clip.mp4 -o assets/hero.svg --cols 110 --fps 12

Then in the README:

    <img src="./assets/hero.svg" width="100%" alt="">
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
    from PIL import Image, ImageEnhance
except ImportError:
    sys.exit("Pillow is required:  python3 -m pip install pillow")


# Ramps run dark -> bright. Index 0 is what the background shows through.
CHARSETS = {
    "blocks": " ░▒▓█",
    "classic": " .:-=+*#%@",
    "dense": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@",
    "binary": " .01",
    "kana": " ・レツカメネミウシヨロアエオ",
    "dots": " ⠂⠆⠇⠏⠟⠿⡿⣿",
}

# name -> (background, gradient stops, glow colour)
THEMES = {
    "tokyo-night": ("#0d1117", ["#7aa2f7", "#bb9af7", "#f7768e"], "#7aa2f7"),
    "matrix": ("#000000", ["#00ff7f", "#00c853", "#004d24"], "#00ff7f"),
    "sakura": ("#0d1117", ["#ff9ec4", "#ffc0cb", "#c792ea"], "#ff9ec4"),
    "ghoul": ("#08080a", ["#e0e0e0", "#9aa0a6", "#c0392b"], "#c0392b"),
    "dracula": ("#282a36", ["#bd93f9", "#ff79c6", "#8be9fd"], "#bd93f9"),
    "ice": ("#0b1622", ["#89ddff", "#82aaff", "#c792ea"], "#89ddff"),
    "amber": ("#0c0c0c", ["#ffb000", "#ff8c00", "#7a3d00"], "#ffb000"),
    "mono": ("#0d1117", ["#e6edf3", "#e6edf3", "#e6edf3"], "#e6edf3"),
    # Built around #7C3AED — the accent already used on chandreshhere.com.
    "violet": ("#0a0a0f", ["#7c3aed", "#a78bfa", "#22d3ee"], "#7c3aed"),
    "violet-warm": ("#0a0a0f", ["#7c3aed", "#c084fc", "#f472b6"], "#a855f7"),
}

# Monospace advance width / line height, as a fraction of font-size. These are
# the numbers we lay the grid out on; textLength pins each row to them so the
# art stays aligned even if the viewer falls back to a different mono font.
CHAR_W = 0.60
LINE_H = 1.05


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def probe_aspect(src: Path) -> float:
    """Return height/width of the source, accounting for anamorphic pixels."""
    try:
        out = run([
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,sample_aspect_ratio",
            "-of", "json", str(src),
        ]).stdout
        s = json.loads(out)["streams"][0]
        w, h = int(s["width"]), int(s["height"])
        sar = s.get("sample_aspect_ratio", "1:1")
        if sar and ":" in sar and "0" not in sar.split(":"):
            sn, sd = (int(x) for x in sar.split(":"))
            w = w * sn // sd
        return h / w
    except Exception:
        return 9 / 16


def crop_filter(top: float, bottom: float, left: float, right: float) -> str:
    """ffmpeg crop expression from percentages, or '' if nothing to crop."""
    if not any((top, bottom, left, right)):
        return ""
    w = f"iw*{(100 - left - right) / 100:.6f}"
    h = f"ih*{(100 - top - bottom) / 100:.6f}"
    return f"crop={w}:{h}:iw*{left / 100:.6f}:ih*{top / 100:.6f},"


def extract_frames(src: Path, tmp: Path, cols: int, rows: int, fps: float,
                   start: float | None, duration: float | None,
                   crop: str = "") -> list[Path]:
    cmd = ["ffmpeg", "-v", "error", "-y"]
    if start:
        cmd += ["-ss", str(start)]
    if duration:
        cmd += ["-t", str(duration)]
    cmd += [
        "-i", str(src),
        # Scale straight to the grid — no aspect preservation here on purpose.
        # `rows` was already derived from the source aspect *and* the character
        # cell's 0.6:1.05 ratio, so one pixel == one character and the art comes
        # out correctly proportioned once it's rendered as text.
        "-vf", f"fps={fps},{crop}scale={cols}:{rows}:flags=area,format=gray",
        str(tmp / "f%05d.png"),
    ]
    run(cmd)
    return sorted(tmp.glob("f*.png"))


def frame_to_rows(path: Path, ramp: str, invert: bool, contrast: float,
                  gamma: float) -> list[str]:
    img = Image.open(path).convert("L")
    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)

    n = len(ramp) - 1
    lut = []
    for v in range(256):
        x = (v / 255.0) ** gamma
        if invert:
            x = 1.0 - x
        lut.append(ramp[min(n, max(0, round(x * n)))])

    px = img.load()
    w, h = img.size
    return ["".join(lut[px[x, y]] for x in range(w)) for y in range(h)]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(frames: list[list[str]], cols: int, rows: int, theme: str,
              font_size: float, dur: float, glow: bool, title: str) -> str:
    bg, stops, glow_col = THEMES[theme]
    pad = font_size * 1.2
    char_w = font_size * CHAR_W
    line_h = font_size * LINE_H
    w = cols * char_w + pad * 2
    h = rows * line_h + pad * 2
    n = len(frames)
    slot = 100.0 / n  # percentage of the loop each frame owns

    grad = "".join(
        f'<stop offset="{i / max(1, len(stops) - 1):.3f}" stop-color="{c}"/>'
        for i, c in enumerate(stops)
    )

    delays = "".join(
        f".f{i}{{animation-delay:{i * dur / n:.4f}s}}" for i in range(n)
    )

    filt = ""
    if glow:
        filt = (
            f'<filter id="glow" x="-20%" y="-20%" width="140%" height="140%">'
            f'<feGaussianBlur stdDeviation="{font_size * 0.14:.2f}" result="b"/>'
            f'<feFlood flood-color="{glow_col}" flood-opacity="0.55"/>'
            f'<feComposite in2="b" operator="in" result="g"/>'
            f'<feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge>'
            f"</filter>"
        )

    out: list[str] = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
        f'viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="{esc(title)}">'
    )
    out.append(f"<title>{esc(title)}</title>")
    out.append(
        "<defs>"
        f'<linearGradient id="ink" x1="0" y1="0" x2="1" y2="1">{grad}</linearGradient>'
        f"{filt}"
        "</defs>"
    )
    out.append("<style>"
               "text{"
               "font-family:ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,"
               "'DejaVu Sans Mono','Liberation Mono',monospace;"
               f"font-size:{font_size:g}px;font-weight:600;"
               "white-space:pre;dominant-baseline:hanging}"
               f".f{{opacity:0;animation:pl {dur:g}s steps(1,end) infinite}}"
               f"@keyframes pl{{0%{{opacity:1}}{slot:.4f}%{{opacity:0}}100%{{opacity:0}}}}"
               "@media (prefers-reduced-motion:reduce){"
               ".f{animation:none}.f0{opacity:1}}"
               f"{delays}"
               "</style>")
    out.append(f'<rect width="100%" height="100%" fill="{bg}" rx="{font_size:.0f}"/>')

    gopen = '<g fill="url(#ink)"' + (' filter="url(#glow)"' if glow else "") + ">"
    out.append(gopen)

    text_w = cols * char_w
    for i, rowlist in enumerate(frames):
        parts = [f'<text class="f f{i}" x="{pad:.1f}" y="{pad:.1f}" xml:space="preserve">']
        for j, line in enumerate(rowlist):
            dy = 0 if j == 0 else line_h
            parts.append(
                f'<tspan x="{pad:.1f}" dy="{dy:.2f}" textLength="{text_w:.1f}" '
                f'lengthAdjust="spacingAndGlyphs">{esc(line)}</tspan>'
            )
        parts.append("</text>")
        out.append("".join(parts))

    out.append("</g></svg>")
    return "".join(out)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Video/GIF -> self-animating ASCII SVG for a GitHub README.")
    p.add_argument("source", help="input video, GIF, or 'demo' for a built-in test clip")
    p.add_argument("-o", "--out", default="assets/ascii.svg")
    p.add_argument("--cols", type=int, default=110, help="width in characters")
    p.add_argument("--fps", type=float, default=12)
    p.add_argument("--start", type=float, help="seek this many seconds in")
    p.add_argument("--duration", type=float, default=6.0, help="seconds to convert")
    p.add_argument("--charset", default="blocks", choices=sorted(CHARSETS))
    p.add_argument("--theme", default="tokyo-night", choices=sorted(THEMES))
    p.add_argument("--font-size", type=float, default=10.0)
    p.add_argument("--contrast", type=float, default=1.35)
    p.add_argument("--gamma", type=float, default=0.85,
                   help="<1 lifts shadows, >1 crushes them")
    p.add_argument("--invert", action="store_true",
                   help="for light art on a light source")
    p.add_argument("--glow", action="store_true", help="CRT bloom")
    p.add_argument("--title", default="ascii animation")
    p.add_argument("--crop-top", type=float, default=0, metavar="PCT",
                   help="chop this %% off the top — burnt-in captions turn into "
                        "noise once they're rendered as characters")
    p.add_argument("--crop-bottom", type=float, default=0, metavar="PCT")
    p.add_argument("--crop-left", type=float, default=0, metavar="PCT")
    p.add_argument("--crop-right", type=float, default=0, metavar="PCT")
    a = p.parse_args()

    for name, v in (("--crop-top", a.crop_top), ("--crop-bottom", a.crop_bottom),
                    ("--crop-left", a.crop_left), ("--crop-right", a.crop_right)):
        if not 0 <= v < 100:
            sys.exit(f"{name} must be between 0 and 100, got {v}")
    if a.crop_top + a.crop_bottom >= 100 or a.crop_left + a.crop_right >= 100:
        sys.exit("crop percentages leave nothing of the frame")

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found — brew install ffmpeg")

    tmp = Path(tempfile.mkdtemp(prefix="asciisvg-"))
    try:
        if a.source == "demo":
            src = tmp / "demo.mp4"
            run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                 "-i", f"life=s=320x180:mold=10:r={a.fps}:ratio=0.1:death_color=#202020"
                       ":life_color=#ffffff",
                 "-t", str(a.duration), "-pix_fmt", "yuv420p", str(src)])
        else:
            src = Path(a.source).expanduser()
            if not src.exists():
                sys.exit(f"no such file: {src}")

        # The crop changes the aspect, so fold it in before deriving rows —
        # otherwise the art comes out stretched along one axis.
        keep_h = (100 - a.crop_top - a.crop_bottom) / 100
        keep_w = (100 - a.crop_left - a.crop_right) / 100
        aspect = probe_aspect(src) * keep_h / keep_w
        rows = max(4, round(a.cols * aspect * (CHAR_W / LINE_H)))
        crop = crop_filter(a.crop_top, a.crop_bottom, a.crop_left, a.crop_right)
        paths = extract_frames(src, tmp, a.cols, rows, a.fps, a.start,
                               a.duration, crop)
        if not paths:
            sys.exit("ffmpeg produced no frames — check --start/--duration")

        ramp = CHARSETS[a.charset]
        frames = [frame_to_rows(f, ramp, a.invert, a.contrast, a.gamma) for f in paths]

        svg = build_svg(frames, a.cols, rows, a.theme, a.font_size,
                        len(frames) / a.fps, a.glow, a.title)

        out = Path(a.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(svg, encoding="utf-8")

        kb = len(svg.encode()) / 1024
        print(f"wrote {out}  ({a.cols}x{rows} chars, {len(frames)} frames, "
              f"{len(frames) / a.fps:.1f}s loop, {kb:.0f} KB)")
        if kb > 2048:
            print("  ! over 2 MB — GitHub's image proxy may refuse it. "
                  "Drop --cols, --fps or --duration.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
