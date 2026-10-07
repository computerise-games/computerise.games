#!/usr/bin/env python3
"""Applies one New Worlds release to releases.html.

    tools/add_release.py 0.2.0 2026-10-08 [path/to/v0.2.0.md]

- The demo version tags (between <!-- demo-version --> markers) become vX.Y.Z.
- The Web Demo table gets a row for it, newest first (once only).
- With a notes file, its card is written - replacing that version's card if
  there is one, or going in above the older notes. img/banner-vX.Y.Z.png, if
  the site has one, heads the card in place of the notes' opening line.

Run by the game repo's release workflow on a final release
(tools/publish-site.sh there), and by hand for anything it missed.

A notes file is Markdown of this shape, the same one the GitHub Release uses:

    # Voxel Worlds

    All worlds, ships and stations now have 3D voxel models!

    ## Voxel worlds
    - Planets are voxels up close...
"""

import datetime
import html
import os
import re
import sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(SITE, "releases.html")


def inline(text):
    """Escapes a line of notes, keeping `code` and **bold**."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", out)


def parse_notes(path):
    title, lede, groups = "", [], []
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip()
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("## "):
            groups.append((line[3:].strip(), []))
        elif line.startswith("- "):
            if not groups:
                groups.append(("", []))
            groups[-1][1].append(line[2:].strip())
        elif line.startswith("  ") and groups and groups[-1][1]:
            groups[-1][1][-1] += " " + line.strip()
        elif line and not groups:
            lede.append(line.strip())
    if not title:
        sys.exit(f"{path}: no '# Title' line")
    return title, " ".join(lede), groups


def card(version, notes_path):
    title, lede, groups = parse_notes(notes_path)
    anchor = "v" + version.replace(".", "-")
    lines = [
        f'    <article class="release" id="{anchor}">',
        f'      <h2 class="pixel">{inline(title)} <span class="tag pixel">v{version}</span></h2>',
    ]
    banner = f"img/banner-v{version}.png"
    if os.path.exists(os.path.join(SITE, banner)):
        alt = f"{title}, v{version}" + (f": {lede}" if lede else "")
        lines += [
            f'      <img class="release-art" src="{banner}" width="1920" height="720" loading="lazy"',
            f'           alt="{html.escape(alt)}">',
        ]
    elif lede:
        lines.append(f'      <p class="release-lede">{inline(lede)}</p>')
    lines.append('      <div class="notes">')
    for name, items in groups:
        if name:
            lines.append(f'        <h3 class="pixel">{inline(name)}</h3>')
        lines.append("        <ul>")
        lines += [f"          <li>{inline(item)}</li>" for item in items]
        lines.append("        </ul>")
    lines += ["      </div>", "    </article>"]
    return "\n".join(lines) + "\n"


def main(argv):
    if len(argv) not in (3, 4):
        sys.exit(__doc__)
    version = argv[1].lstrip("v")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        sys.exit(f"{argv[1]} isn't X.Y.Z - only final releases go on the page")
    day = datetime.date.fromisoformat(argv[2])
    page = open(PAGE, encoding="utf-8").read()

    page, tags = re.subn(
        r"(<!-- demo-version -->)v[^<]*(<!-- /demo-version -->)",
        rf"\1v{version}\2",
        page,
    )
    if not tags:
        sys.exit("releases.html has no <!-- demo-version --> markers")

    if f"<td>v{version}</td>" not in page:
        row = (
            f"          <tr><td>v{version}</td><td>Web demo</td>"
            f"<td>{day.day} {day.strftime('%b %Y')}</td></tr>\n"
        )
        page, rows = re.subn(r"(<!-- versions -->\n)", lambda m: m.group(1) + row, page, count=1)
        if not rows:
            sys.exit("releases.html has no <!-- versions --> marker")

    if len(argv) == 4:
        new = card(version, argv[3])
        anchor = "v" + version.replace(".", "-")
        page, replaced = re.subn(
            rf'    <article class="release" id="{anchor}">.*?</article>\n',
            lambda m: new,
            page,
            count=1,
            flags=re.S,
        )
        if not replaced:
            page, added = re.subn(
                r"(<!-- notes -->\n)", lambda m: m.group(1) + new, page, count=1
            )
            if not added:
                sys.exit("releases.html has no <!-- notes --> marker")

    open(PAGE, "w", encoding="utf-8").write(page)
    print(f"releases.html: v{version}, {day.isoformat()}")


if __name__ == "__main__":
    main(sys.argv)
