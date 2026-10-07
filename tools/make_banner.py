#!/usr/bin/env python3
"""Renders a release banner from a game screenshot.

    tools/make_banner.py 0.3.0 path/to/v0.3.0.md path/to/screenshot.png [out.png]
        [--date 2026-10-08]

Fills banners/release.html with the notes' title and opening line, the
version, the release date (default today) and the screenshot (cropped to
cover), and screenshots it with
headless Chrome at 1920x720 - by default to img/banner-v<version>.png, the
file add_release.py puts at the head of that release's card.

Run by the game repo's release.sh (a final release pushes the banner here
before its tag), and by hand to preview one. CHROME names the browser if
it isn't google-chrome, chromium or chromium-browser on PATH.
"""

import datetime
import functools
import http.server
import os
import shutil
import string
import subprocess
import sys
import tempfile
import threading

sys.dont_write_bytecode = True  # no tools/__pycache__ in the site
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from add_release import SITE, inline, nice_date, parse_notes  # noqa: E402

TEMPLATE = os.path.join(SITE, "banners", "release.html")
WIDTH, HEIGHT = 1920, 720


def chrome():
    names = [os.environ.get("CHROME"), "google-chrome", "chromium", "chromium-browser"]
    for name in filter(None, names):
        path = shutil.which(name)
        if path:
            return path
    sys.exit("no Chrome found - set CHROME to the browser's path")


def render(version, day, notes_path, art_path, out_path):
    title, lede, _ = parse_notes(notes_path)
    # Served from the site root, so the template's ../../fonts resolve.
    build = tempfile.mkdtemp(prefix="_build-", dir=os.path.join(SITE, "banners"))
    profile = tempfile.mkdtemp(prefix="banner-chrome-")
    server = None
    try:
        art = "art" + os.path.splitext(art_path)[1].lower()
        shutil.copy(art_path, os.path.join(build, art))
        page = string.Template(open(TEMPLATE, encoding="utf-8").read()).substitute(
            version=version, date=nice_date(day), title=inline(title), lede=inline(lede), art=art
        )
        open(os.path.join(build, "index.html"), "w", encoding="utf-8").write(page)

        handler = functools.partial(QuietHandler, directory=SITE)
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = "http://127.0.0.1:%d/banners/%s/index.html" % (
            server.server_address[1],
            os.path.basename(build),
        )
        subprocess.run(
            [
                chrome(),
                "--headless=new",
                "--hide-scrollbars",
                "--no-first-run",
                "--user-data-dir=" + profile,
                "--window-size=%d,%d" % (WIDTH, HEIGHT),
                "--virtual-time-budget=3000",
                "--screenshot=" + os.path.abspath(out_path),
                url,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    finally:
        if server:
            server.shutdown()
        shutil.rmtree(build, ignore_errors=True)
        shutil.rmtree(profile, ignore_errors=True)
    if not os.path.exists(out_path):
        sys.exit(f"Chrome didn't write {out_path}")
    print(f"{out_path}: {title}, v{version}")


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main(argv):
    day = datetime.date.today()
    if "--date" in argv:
        at = argv.index("--date")
        if at + 1 >= len(argv):
            sys.exit(__doc__)
        day = datetime.date.fromisoformat(argv[at + 1])
        argv = argv[:at] + argv[at + 2 :]
    if len(argv) not in (4, 5):
        sys.exit(__doc__)
    version = argv[1].lstrip("v")
    out = argv[4] if len(argv) == 5 else os.path.join(SITE, "img", f"banner-v{version}.png")
    render(version, day, argv[2], argv[3], out)


if __name__ == "__main__":
    main(sys.argv)
