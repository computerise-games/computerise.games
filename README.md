# computerise.games

The computerise studio site: the New Worlds landing page (`index.html`)
and its releases page (`releases.html`). Served by GitHub Pages at https://computerise.games.

## Preview locally

    python3 -m http.server 8070    # then open http://localhost:8070

## Deploy

GitHub Pages serves `master` from the repo root; `CNAME` holds the custom
domain and `.nojekyll` skips the Jekyll build.

One-time setup:

1. Push this repo to GitHub, then Settings > Pages > Source: "Deploy from a
   branch", `master`, `/ (root)`.
2. At the registrar, point the apex domain at GitHub Pages:
   - `A` records for `computerise.games`: 185.199.108.153, 185.199.109.153,
     185.199.110.153, 185.199.111.153
   - `AAAA` records: 2606:50c0:8000::153, 2606:50c0:8001::153,
     2606:50c0:8002::153, 2606:50c0:8003::153
   - `CNAME` for `www`: `<owner>.github.io`
3. Once DNS resolves, tick "Enforce HTTPS" in Settings > Pages.
4. Optional, recommended: verify the domain under the account's
   Settings > Pages so no other repo can claim it.

## Placeholders to fill in

- **Steam:** both pages link to
  `https://store.steampowered.com/app/STEAM_APP_ID/New_Worlds/`; replace
  `STEAM_APP_ID` once the Coming Soon page exists.
- **Social:** the Follow buttons in `index.html` point at `#follow`.
- **Releases:** `releases.html`'s table is written by hand; add a row per
  release.

## Assets

- `video/new-worlds-trailer.mp4`, `video/new-worlds-trailer-1080p30.mp4`
  and `video/new-worlds-trailer-720p30.mp4`: the landing page's hero, using
  the game repo's trailer (`tools/capture/edit.py`) re-encoded as 1080p60,
  1080p30 and 720p30 H.264/AAC MP4s with `faststart`. Run
  `tools/encode-trailer-variants.sh [high-quality-input.mp4]` after replacing
  the high-quality source to rebuild the two smaller files. `trailer.js` picks
  a source from the browser's Network Information estimate and switches while
  preserving playback position when the estimate changes; browsers without
  that API use the 1080p30 encode. "Watch the trailer" opens the video itself
  in fullscreen with the browser's native controls. The old hero still,
  `terra-launch-transit`, is its poster and the gallery page's header now.
- `img/*.webp`: full-size and 960px copies of stills from the game repo's
  `docs/media/screenshots/`. `og.jpg` is the 1200x675 link-preview image.
- `img/title/`: the main menu's title layers (`ui/title_logo/`), Terra's
  loading loop sheet and the player ship sprite, drawn live by
  `title-logo.js` - a port of the game's `ui/title_logo.gd`. Re-copy them
  if the game's title is rebaked.
- From the game repo, copied as-is:
  - `fonts/`: Silkscreen (headings, buttons) and VT323 (the game's panel
    font), SIL OFL 1.1 - their licences are in `licenses/`.
  - `img/icons/`, `img/features/`: UI glyphs from `ui/icons/`.
  - `img/ships/`: hull sprites from `player/` and `spacecraft/ships/`,
    drawn at 2 CSS px per texel so every hull shares one scale.
  - `img/favicon.png`: the game's app icon.
- `img/starfield.png`: the page background, a tile scattered from the
  game's `sky/stars/` sprites (one art pixel per texel block, the
  starfield's own colour weights).
- Colours: the sky, and `ui/theme.tres`' cream panels, brown edges and
  dark button wells.
- `img/social/`: brand icons from Simple Icons (CC0,
  https://simpleicons.org); the brands' own trade marks still apply.
