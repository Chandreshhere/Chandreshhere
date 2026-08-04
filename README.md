<!--
  Chandresh Delwar — profile README
  Lives at github.com/Chandreshhere/Chandreshhere

  What GitHub's sanitiser allows here:
    OK    <img> <a> <div align> <picture> <details> <table> <br> animated GIF
          animated SVG (its CSS lives inside the .svg, out of reach)
    GONE  <script> <video> <iframe> <style> class= onclick=

  Accent is #7C3AED end to end — hero, typing header, every stat card.

  SECTION ORDER (top to bottom):
    hero → header → about+video → dashboard → snake → stack → work → details
-->

<div align="center">

<!-- ── ASCII HERO ──────────────────────────────────────────────────
     Source: ~/Desktop/top.mp4. Regenerate with:
       python3 tools/ascii_svg.py ~/Desktop/top.mp4 -o assets/hero.svg \
         --cols 120 --fps 10 --duration 5.4 --charset blocks \
         --contrast 1.6 --gamma 1.0 --theme violet --glow --crop-bottom 22

     --duration 5.4 is deliberate: the source cuts to black at ~5.5s and
     then to unrelated green/blue static, so the loop stops before that.
     --charset blocks (5 tonal steps) beats the finer ramps here because
     the subject is high-contrast against a flat background — the short
     ramp keeps the silhouette solid where a long one just adds noise. -->
<img src="./assets/hero.svg" width="100%" alt="">

<br><br>

# Chandresh Delwar

**Frontend Engineer · UI/UX Designer · Creative Developer**

<img src="https://readme-typing-svg.demolab.com?font=Lexend&weight=600&size=22&pause=1000&duration=2600&color=7C3AED&center=true&vCenter=true&width=700&lines=Building+Premium+Web+Experiences;Next.js+%2B+GSAP+Developer;Design+Systems+%26+Motion;Always+Learning+Something+New" alt="">

<br>

<!-- Portfolio only. The GitHub badge was removed — it linked to the page
     the visitor is already standing on. -->
<a href="https://www.chandreshhere.com"><img src="https://img.shields.io/badge/Portfolio-7C3AED?style=for-the-badge&logoColor=white" alt="Portfolio"></a>

<!-- LinkedIn + email are held back until the handles are filled in — a live
     badge pointing at linkedin.com/in/__LINKEDIN__ is worse than no badge.
     Replace the two placeholders below and delete these comment markers.
<a href="https://linkedin.com/in/__LINKEDIN__"><img src="https://img.shields.io/badge/LinkedIn-18181B?style=for-the-badge&logo=linkedin&logoColor=A78BFA" alt="LinkedIn"></a> <a href="mailto:__EMAIL__"><img src="https://img.shields.io/badge/Email-18181B?style=for-the-badge&logo=gmail&logoColor=A78BFA" alt="Email"></a>
-->

</div>

<br><br>

<!-- ══════════════════════════════════════════════════════════════
     ABOUT — video sits on the right, text wraps around it.
     `align="right"` is the only float GitHub's sanitiser keeps, and
     <br clear="right"> is what stops the NEXT section from riding up
     into the gap beside it.
     ══════════════════════════════════════════════════════════════ -->

<!-- Source: "lyffy video.mp4". Top 8% cropped to remove the burnt-in
     "Luffy comiendo" caption — 5% left emoji fragments along the top edge.
     Then squared, quantised to 48 colours and nearest-neighbour upscaled so
     the pixels stay hard-edged. -->
<img align="right" width="340" src="./assets/luffy.gif" alt="">

### About

I build premium websites and interactive product experiences — combining
**design**, **motion**, and **engineering** into interfaces that are fast,
responsive, and genuinely nice to use.

Right now I'm going deep on UI engineering, animation, design systems, and
product thinking, with the goal of being one of the best creative frontend
developers around.

```
design  →  motion  →  code  →  ship
```

<br clear="right">

<br>

<!-- ══════════════════════════════════════════════════════════════
     DASHBOARD — moved up, directly under About.

     One palette across every card: same bg, same accent, same
     borderless treatment, so the widgets read as one panel rather
     than four bolted-on services.

     NOTE: github-readme-stats.vercel.app returns 503 most days
     (shared Vercel quota, exhausted). The mirror below responds.
     Permanent fix in SETUP.md §7.
     ══════════════════════════════════════════════════════════════ -->

<div align="center">

### Dashboard

<!-- Heads-up: this card renders as "Moon's GitHub Stats" — that's the display
     name on your GitHub account, which reads oddly on a profile branded
     "Chandresh Delwar". `custom_title` is set below but THIS MIRROR IGNORES IT
     (it's an outdated fork). Two real fixes: rename yourself at
     github.com/settings/profile, or self-deploy the card (SETUP.md §7), where
     custom_title does work. The param is left in so it takes effect the
     moment you switch to your own instance. -->
<img width="49%" src="https://github-readme-stats-sigma-five.vercel.app/api?username=Chandreshhere&show_icons=true&hide_border=true&bg_color=0A0A0F&title_color=7C3AED&icon_color=A78BFA&text_color=A1A1AA&ring_color=7C3AED&include_all_commits=true&rank_icon=github&custom_title=GitHub%20Stats" alt="">
<img width="49%" src="https://streak-stats.demolab.com?user=Chandreshhere&hide_border=true&background=0A0A0F&stroke=27272A&ring=7C3AED&fire=A78BFA&currStreakLabel=7C3AED&sideLabels=A1A1AA&dates=52525B&currStreakNum=FAFAFA&sideNums=FAFAFA" alt="">

<br><br>

<img width="99%" src="https://github-readme-activity-graph.vercel.app/graph?username=Chandreshhere&bg_color=0A0A0F&color=FAFAFA&line=7C3AED&point=A78BFA&area=true&area_color=1E1B2E&hide_border=true&custom_title=Contribution%20Graph" alt="">

<br><br>

<img width="42%" src="https://github-readme-stats-sigma-five.vercel.app/api/top-langs/?username=Chandreshhere&layout=compact&langs_count=8&hide_border=true&bg_color=0A0A0F&title_color=7C3AED&text_color=A1A1AA&card_width=380" alt="">

<br><br>

### Trophies

<!-- The canonical github-profile-trophy.vercel.app returns 402 (the
     maintainer's Vercel account is over its billing limit) and renders as a
     broken image. This is a working deployment of the same project.
     `discord` is the closest built-in theme to our violet — the trophy
     service has no custom-colour params, so it's theme presets only.

     The rank list is every grade EXCEPT unearned — without it you get five
     grey "Unknown / 0pt" tiles padding out the row, which reads as a gap
     rather than an achievement. There's no "-UNKNOWN" exclusion syntax that
     works on this service, so the grades are listed positively instead. -->
<img width="99%" src="https://github-trophies.vercel.app/?username=Chandreshhere&theme=discord&no-frame=true&no-bg=true&column=7&margin-w=8&margin-h=8&rank=SECRET,SSS,SS,S,AAA,AA,A,B,C" alt="">

<br><br>

<!-- ══════════════════════════════════════════════════════════════
     SNAKE — moved up, straight after the dashboard. It's the same
     contribution data the graph above shows, so the two belong
     together rather than separated by the stack and project lists.
     Generated by .github/workflows/snake.yml into the `output`
     branch, refreshed every 12h.
     ══════════════════════════════════════════════════════════════ -->

### Contribution Snake

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Chandreshhere/Chandreshhere/output/snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Chandreshhere/Chandreshhere/output/snake.svg">
  <img alt="snake eating my contribution graph" src="https://raw.githubusercontent.com/Chandreshhere/Chandreshhere/output/snake-dark.svg">
</picture>

<br><br>

<!-- ── SPOTIFY ─────────────────────────────────────────────────────
     This one CANNOT be a plain URL like the others — it needs your
     Spotify OAuth, so it only works after you deploy your own instance
     and connect your account (~5 min, SETUP.md §8). Uncomment once you
     have your UID, otherwise it renders as a broken image.

<a href="https://open.spotify.com/user/__SPOTIFY_UID__">
  <img width="46%" src="https://spotify-github-profile.kittinanx.com/api/view?uid=__SPOTIFY_UID__&cover_image=true&theme=novatorem&bar_color=7C3AED&bar_color_cover=true" alt="Now playing on Spotify">
</a>
-->

</div>

<br><br>

<!-- ══════════════════════════════════════════════════════════════
     STACK — your draft listed these twice ("Tech Stack" and "My
     Toolbox" are the same list). Once, as icons, reads far better
     than thirty bullet points.
     ══════════════════════════════════════════════════════════════ -->

<div align="center">

### Stack

<img src="https://skillicons.dev/icons?i=react,nextjs,ts,js,html,css,tailwind&theme=dark" alt="">
<br>
<img src="https://skillicons.dev/icons?i=figma,git,github,vscode,vercel,nodejs&theme=dark" alt="">

<br><br>

**Motion** &nbsp;·&nbsp; GSAP &nbsp;·&nbsp; ScrollTrigger &nbsp;·&nbsp; SplitText &nbsp;·&nbsp; Framer Motion &nbsp;·&nbsp; Lenis

**State &amp; Data** &nbsp;·&nbsp; Zustand &nbsp;·&nbsp; Axios

**Design** &nbsp;·&nbsp; UI &nbsp;·&nbsp; UX &nbsp;·&nbsp; Wireframing &nbsp;·&nbsp; Prototyping &nbsp;·&nbsp; Design Systems

</div>

<br><br>

<!-- ══════════════════════════════════════════════════════════════
     PROJECTS — link them. An unlinked project list reads as
     aspiration; a linked one reads as evidence.
     ══════════════════════════════════════════════════════════════ -->

### Featured Work

<!-- These are four of your real repos that already have live Vercel
     deployments. I have NOT written descriptions for them, because I don't
     know what they are and inventing copy for your own projects would be
     worse than leaving it blank. Replace each "..." with one honest line,
     and swap in different repos if these aren't your strongest.

     Other deployed repos to choose from: ciao-2.0, icon-reality, evara,
     closet-web, ninehauk, digexa, nestinwoods, lexops, cleanse-new,
     circle-media, ud-store, softcorner, artisan---co, namanmusic. -->

| | |
|---|---|
| **[syncquic](https://github.com/Chandreshhere/syncquic)** · [live ↗](https://synquic.vercel.app)<br><sub>...</sub> | **[roccia](https://github.com/Chandreshhere/roccia-new)** · [live ↗](https://roccia-new.vercel.app)<br><sub>...</sub> |
| **[underdawg brand portal](https://github.com/Chandreshhere/underdawg-brand-portal)** · [live ↗](https://underdawg-brand-portal.vercel.app)<br><sub>...</sub> | **[wow](https://github.com/Chandreshhere/wow)** · [live ↗](https://wow-sigma-one.vercel.app)<br><sub>...</sub> |

<br>

<!-- ══════════════════════════════════════════════════════════════
     THE LONG LISTS — kept, but folded away. <details> is on
     GitHub's allowlist and collapses by default.
     ══════════════════════════════════════════════════════════════ -->

<details>
<summary><b>Currently learning</b></summary>
<br>

Frontend architecture · design systems · accessibility · backend fundamentals ·
performance optimisation · product design · motion design · clean code

</details>

<details>
<summary><b>Goals</b></summary>
<br>

- Master frontend engineering
- Build award-winning websites
- Learn product thinking
- Improve backend fundamentals
- Create open-source components
- Build scalable design systems
- Launch my own products

</details>

<details>
<summary><b>How I work</b></summary>
<br>

`research` → `wireframe` → `design` → `prototype` → `develop` → `animate` → `optimise` → `launch`

Great products aren't built with code alone — they need great design, UX,
performance, motion, typography, and attention to detail.

</details>

<br><br>

<div align="center">

<img src="./assets/footer.svg" width="100%" alt="">

<sub><i>"Design is how it works. Motion is how it feels. Code is how it comes alive."</i></sub>

<br><br>

<img src="https://komarev.com/ghpvc/?username=Chandreshhere&label=profile+views&color=7C3AED&style=flat-square" alt="">

<br><br>

<sub>Designed &amp; built by <b>Chandresh Delwar</b> · <a href="https://www.chandreshhere.com">chandreshhere.com</a></sub>

</div>
