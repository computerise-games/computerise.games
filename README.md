# computerise.games

The Computerise studio site: a single static page listing New Worlds as
coming soon. Served by GitHub Pages at https://computerise.games.

## Preview locally

    python3 -m http.server 8070    # then open http://localhost:8070

## Deploy

GitHub Pages serves `main` from the repo root; `CNAME` holds the custom
domain and `.nojekyll` skips the Jekyll build.

One-time setup:

1. Push this repo to GitHub, then Settings > Pages > Source: "Deploy from a
   branch", `main`, `/ (root)`.
2. At the registrar, point the apex domain at GitHub Pages:
   - `A` records for `computerise.games`: 185.199.108.153, 185.199.109.153,
     185.199.110.153, 185.199.111.153
   - `AAAA` records: 2606:50c0:8000::153, 2606:50c0:8001::153,
     2606:50c0:8002::153, 2606:50c0:8003::153
   - `CNAME` for `www`: `<owner>.github.io`
3. Once DNS resolves, tick "Enforce HTTPS" in Settings > Pages.
4. Optional, recommended: verify the domain under the account's
   Settings > Pages so no other repo can claim it.

## Screenshots

`img/` holds WebP copies (full size plus 960px) of stills from the game
repo's `docs/media/screenshots/`. `og.jpg` is the 1200x675 link-preview
image.
