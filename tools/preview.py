#!/usr/bin/env python3
"""
preview.py — see the README the way GitHub will render it, before pushing.

This does NOT approximate the rendering: it POSTs the file to GitHub's own
markdown API, so the HTML you get back is the same HTML the site produces,
including whatever the sanitiser decided to strip. Local ./assets paths are
rewritten to absolute file:// URLs so your animations show up; the remote stat
cards load live over the network.

    python3 tools/preview.py            # render + open in your browser
    python3 tools/preview.py --shot     # also save a full-page PNG

No auth needed (anonymous API, ~60 requests/hour).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Approximation of GitHub's dark README chrome — enough to judge spacing,
# contrast and whether the cards line up.
CSS = """
:root{color-scheme:dark}
body{margin:0;background:#010409;font:16px/1.5 -apple-system,BlinkMacSystemFont,
"Segoe UI",Noto Sans,Helvetica,Arial,sans-serif;color:#e6edf3}
.wrap{max-width:1012px;margin:32px auto;padding:0 16px}
.card{border:1px solid #3d444d;border-radius:6px;background:#0d1117;padding:32px}
.markdown-body img{max-width:100%;vertical-align:middle}
.markdown-body h3{margin:24px 0 16px;padding-bottom:.3em;font-size:1.25em;
font-weight:600;border-bottom:1px solid #3d444d}
.markdown-body p{margin:0 0 16px}
.markdown-body a{color:#4493f8;text-decoration:none}
.markdown-body pre{background:#151b23;border-radius:6px;padding:16px;overflow:auto;
font:13px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace}
.markdown-body code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.markdown-body table{border-collapse:collapse;margin-bottom:16px}
.markdown-body td,.markdown-body th{border:1px solid #3d444d;padding:6px 13px}
.markdown-body sub{color:#9198a1}
.bar{color:#9198a1;font-size:12px;margin:0 0 8px;padding-left:4px}
"""


def render(md: str) -> str:
    req = urllib.request.Request(
        "https://api.github.com/markdown",
        data=json.dumps({"text": md, "mode": "gfm"}).encode(),
        headers={"Content-Type": "application/json",
                 "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode()
    except urllib.error.HTTPError as e:
        if e.code == 403:
            sys.exit("GitHub API rate limit hit (60/hr anonymous). Wait a bit.")
        sys.exit(f"GitHub markdown API returned {e.code}: {e.read().decode()[:200]}")
    except urllib.error.URLError as e:
        sys.exit(f"could not reach GitHub: {e.reason}")


def main() -> int:
    p = argparse.ArgumentParser(description="Preview README.md as GitHub renders it.")
    p.add_argument("readme", nargs="?", default="README.md")
    p.add_argument("-o", "--out", default="preview.html")
    p.add_argument("--shot", action="store_true", help="also save preview.png")
    p.add_argument("--no-open", action="store_true")
    a = p.parse_args()

    src = Path(a.readme).resolve()
    if not src.exists():
        sys.exit(f"no such file: {src}")

    html = render(src.read_text(encoding="utf-8"))

    # Point relative asset paths at the real files on disk.
    root = src.parent.as_uri()
    html = re.sub(r'(src|href)="\./', rf'\1="{root}/', html)

    # github-readme-stats fades its rows in from opacity:0 on a stagger.
    # A headless screenshot catches that at frame zero and the card looks
    # empty when it is fine. Ask for the static variant *in the preview only*
    # so what you see matches what GitHub ends up showing.
    html = re.sub(r'(src="https://github-readme-stats[^"]*?)"',
                  r'\1&disable_animations=true"', html)

    out = Path(a.out).resolve()
    out.write_text(
        f"<!doctype html><meta charset=utf-8><title>README preview</title>"
        f"<style>{CSS}</style><div class=wrap>"
        f"<p class=bar>local preview &middot; GitHub's own renderer &middot; "
        f"remote cards load live</p>"
        f"<div class=card><article class=markdown-body>{html}</article></div></div>",
        encoding="utf-8",
    )
    print(f"wrote {out}")

    if a.shot and Path(CHROME).exists():
        png = out.with_suffix(".png")
        # The stat cards fade their rows in on a stagger. Without letting the
        # compositor finish, the screenshot catches them at opacity 0 and the
        # cards look broken when they aren't.
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                        "--virtual-time-budget=20000",
                        "--run-all-compositor-stages-before-draw",
                        "--window-size=1100,3000",
                        f"--screenshot={png}", out.as_uri()],
                       capture_output=True)
        print(f"wrote {png}")

    if not a.no_open:
        webbrowser.open(out.as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
