# Profile README — setup

For **[github.com/Chandreshhere](https://github.com/Chandreshhere)** · accent `#7C3AED`

---

## 0. The rule that governs all of this

GitHub's markdown renderer strips `<script>`, `<video>`, `<iframe>`, `<style>`,
`class=`, and inline CSS. You **cannot** play a video file in a README.

What survives, and what every good profile actually leans on:

| Works | Why |
|---|---|
| animated **GIF** | it's just an `<img>` and it loops itself |
| animated **SVG** | also an `<img>`, but its CSS keyframes live *inside* the `.svg`, where the sanitiser never looks |
| `<img> <a> <div align> <picture> <details> <table>` | on GitHub's HTML allowlist |

So the ASCII hero at the top is an SVG with 60 baked-in frames that cross-fade
themselves. No JS, no third-party service, nothing to rate-limit.

---

## 1. Publish it

The magic repo name is your username, twice:

```bash
gh auth login                       # not currently authenticated on this machine
gh repo create Chandreshhere --public --clone
cd Chandreshhere
```

Copy `README.md`, `assets/`, `tools/`, `.github/` in, then:

```bash
git add -A && git commit -m "profile readme" && git push
```

It appears on your profile immediately. **Nothing is pushed until you run this** —
everything so far is local.

### Preview before you push

```bash
python3 tools/preview.py            # opens in your browser
python3 tools/preview.py --shot     # also writes preview.png
```

This POSTs the file to GitHub's *own* markdown API, so the HTML is exactly what
the site produces, sanitiser included. Remote cards load live; local assets are
rewritten to `file://`. No auth needed (~60 requests/hour anonymous).

---

## 2. Widgets — what's wired up

| Widget | Status |
|---|---|
| Animated typing banner | ✅ `readme-typing-svg.demolab.com`, Lexend + `#7C3AED` |
| GitHub Stats | ✅ mirror instance (see §7) |
| Streak Stats | ✅ `streak-stats.demolab.com` |
| Activity Graph | ✅ violet line + area |
| Most Used Languages | ✅ compact, 8 langs |
| Profile Trophy | ✅ mirror — canonical instance returns 402 (§7) |
| Visitor Counter | ✅ `komarev.com/ghpvc` |
| Snake Animation | ⚙️ needs the workflow to run once — §6 |
| Spotify | ⚙️ needs your OAuth — §8, commented out until then |

Everything shares one palette: `bg_color=0A0A0F`, `title_color=7C3AED`,
`text_color=A1A1AA`, `hide_border=true`. **Give any new card those same
parameters and it drops straight in.** That consistency is doing more work than
any single widget.

---

## 3. Swap the hero for your own clip

The current hero is a placeholder generated from a synthetic source. Replace it:

```bash
python3 -m pip install pillow     # once
brew install ffmpeg               # once

python3 tools/ascii_svg.py reel.mp4 \
  -o assets/hero.svg \
  --cols 120 --fps 12 --start 8 --duration 5 \
  --charset blocks --theme violet --glow
```

Since you're a motion person, the obvious source is a screen recording of your
own GSAP work — an agency-site scroll sequence in ASCII is a much better flex
than a stock anime clip.

Looks worth trying:

```bash
--charset dots    --theme violet       --glow      # current hero
--charset dense   --theme violet-warm  --contrast 1.8
--charset classic --theme ice          --gamma 0.7
--charset blocks  --theme mono         --contrast 1.6
```

Tuning, in the order you'll need it:

- **`--cols`** — detail. 90 chunky, 120 balanced, 150+ tiny on mobile and huge.
- **`--contrast` / `--gamma`** — the two that fix a muddy result. Raise contrast
  when it's all mid-grey; drop gamma to `0.7` to lift dark footage.
- **`--charset`** — `blocks` reads best small, `dense` has the most tonal steps.
- **`--invert`** — for dark art on a light background.

Pick a shot with a **big, high-contrast subject**. ASCII discards colour and
fine detail: a close-up or a strong silhouette survives, a busy wide shot
becomes noise. The script prints the file size and warns past 2 MB — `cols ×
rows × frames` is the whole cost, so halving `--fps` halves the file.

## 4. The pixel-art GIF

```bash
python3 tools/pixelate.py reel.mp4 -o assets/idle.gif \
  --pixels 200 --colors 32 --duration 4 --grade crt --boomerang
```

`--pixels` is the crunch (120 = chunky sprite, 300 = barely pixelated).
`--colors` 16–32 for retro. `--boomerang` plays forward then reverse so a clip
that doesn't loop cleanly still does. `--grade` offers `crt`, `neon`, `noir`,
`gameboy`, `washed`.

---

## 5. Fill in what's left

```bash
./tools/set-username.sh Chandreshhere <linkedin-handle> <email>
```

Username is already applied. Still open:

- `__LINKEDIN__` and `__EMAIL__` in the header badges
- **Featured Work descriptions** — four real deployed repos are linked
  (`syncquic`, `roccia-new`, `underdawg-brand-portal`, `wow`), each with a `...`
  where a one-line description goes. I deliberately didn't write these: making
  up copy about your own projects would be worse than a blank.

---

## 6. Turn on the snake

`.github/workflows/snake.yml` is included. After the first push:
**Actions** tab → enable workflows → run *Generate contribution snake* once by
hand. It writes to an `output` branch that the README reads from, and refreshes
every 12 hours. The snake image 404s until that first run — expected.

---

## 7. When a card breaks

Two of the popular free instances are unreliable, and both were broken in your
original draft:

| Service | State | Fix |
|---|---|---|
| `github-readme-stats.vercel.app` | **503** most days — shared free Vercel quota, exhausted daily | using a mirror |
| `github-profile-trophy.vercel.app` | **402 Payment Required** — maintainer's billing | using `github-trophies.vercel.app` |

Mirrors are other people's free deployments, so they can vanish too. The
permanent fix is a two-minute self-deploy:

1. Fork [anuraghazra/github-readme-stats](https://github.com/anuraghazra/github-readme-stats)
2. Import the fork at [vercel.com/new](https://vercel.com/new) → Deploy
3. Add a `PAT_1` env var (a GitHub token with `public_repo`) to raise your limits
4. Swap the host in the README for your own `*.vercel.app`

Same procedure for [ryo-ma/github-profile-trophy](https://github.com/ryo-ma/github-profile-trophy).
Then no one else's quota can take your profile down.

## 8. Spotify (optional)

Unlike every other widget, this can't be a plain URL — it needs *your* Spotify
OAuth, so a shared instance can't show your track.

1. [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) →
   Create app → note the Client ID and Secret
2. Fork + deploy [kittinan/spotify-github-profile](https://github.com/kittinan/spotify-github-profile)
   to Vercel with those as env vars
3. Add `<your-deploy>/api/callback` as a Redirect URI in the Spotify dashboard
4. Visit `<your-deploy>/api/login`, authorise, copy the `uid` it gives you
5. Uncomment the Spotify block in the README and replace `__SPOTIFY_UID__`

Caveat worth knowing: it shows "now playing" only while you're actually
listening, and falls back to the last-played track otherwise.

---

## 9. Honest notes on the content

Things I changed from your draft, and why:

**Fifteen `#` sections became six.** Every section was a bullet list, and
"Tech Stack" and "My Toolbox" listed the same tools twice. The long lists aren't
deleted — they're in `<details>` blocks, which are on GitHub's allowlist and
collapse by default. Content preserved, wall removed.

**Projects are linked now.** Your draft listed five projects with no URLs. An
unlinked project list reads as aspiration; a linked one reads as evidence — and
you have 28 repos with live Vercel deployments to link.

**The bigger win isn't this README.** Of your 51 non-fork repos: **3 have a
description, 0 have topics**, and 28 have a live demo URL that nothing points
at. A visitor who likes the profile clicks through to a wall of unlabelled repo
names. Ten minutes adding a one-line description + the live URL + 2–3 topics to
your best ten repos will do more for you than any widget here. Pin six of them
while you're at it.

**Your GitHub display name is "Moon".** So the stats card reads "Moon's GitHub
Stats" on a profile branded "Chandresh Delwar". `custom_title` is set in the
README but the mirror ignores it (outdated fork) — so this only actually
resolves by renaming at
[github.com/settings/profile](https://github.com/settings/profile), or by
self-deploying the card per §7, where the param works.

---

## Troubleshooting

**A card is blank or broken.** Curl it — `curl -o /dev/null -w "%{http_code}"
"<url>"`. 503/402 means that service is down, not your markup.

**The SVG doesn't animate on GitHub.** Confirm it's committed and you're linking
the `.svg` itself. GitHub proxies images through camo and caches hard; a changed
file can take minutes to refresh.

**Badges stack vertically.** Keep the `<a>` tags on **one source line** — a line
break between them becomes a paragraph split.

**ASCII art shears or misaligns.** Shouldn't happen; each row is pinned with
`textLength`. If it does, raise `--font-size` to 12.

**Stat cards look empty in `preview.py --shot`.** Only in the screenshot — those
cards fade in from `opacity:0` and headless Chrome freezes them. The preview
already requests the static variant; the live profile is fine.
