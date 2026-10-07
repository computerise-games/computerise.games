#!/usr/bin/env python3
"""Applies one New Worlds release to releases.html and the home page.

    tools/add_release.py 0.2.0 2026-10-08 [path/to/v0.2.0.md]

- The demo version tags (between <!-- demo-version --> markers) become vX.Y.Z.
- The Web Demo table gets a row for it, newest first (once only).
- With a notes file, its card is written - replacing that version's card if
  there is one, or going in above the older notes. img/banner-vX.Y.Z.png, if
  the site has one, heads the card in place of the notes' opening line (and
  carries the date - tools/make_banner.py). A patch (X.Y.Z, Z > 0) never has
  a banner: its card is a thin one, dated beside its version.
- The home page's release banner (between <!-- latest-release --> markers)
  points at it: version, date and link always. A patch keeps the banner of
  the release it follows; a X.Y.0 also brings its title and opening line,
  and its art when it has img/banner-vX.Y.Z-art.webp (make_banner.py again).

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
INDEX = os.path.join(SITE, "index.html")


LINK = re.compile(
    r"\[(?P<text>[^\]]+)\]\((?P<url>(?:https?://|mailto:)[^)\s]+)\)"
    r"|(?P<bare>https?://[^\s<]+[^\s<.,;:!?)])"
    r"|(?P<email>[\w.+-]+@[\w-]+(?:\.[\w-]+)+)"
)


def link(match):
    if match["text"]:
        return f'<a href="{match["url"]}">{match["text"]}</a>'
    if match["bare"]:
        return f'<a href="{match["bare"]}">{match["bare"]}</a>'
    return f'<a href="mailto:{match["email"]}">{match["email"]}</a>'


def inline(text):
    """Escapes a line of notes, keeping `code` and **bold**, and linking
    [text](url), bare http(s) URLs and email addresses."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"`(.+?)`", r"<code>\1</code>", out)
    return LINK.sub(link, out)


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


def nice_date(day):
    return f"{day.day} {day.strftime('%b %Y')}"


def is_patch(version):
    return int(version.split(".")[2]) > 0


def anchor_of(version):
    return "v" + version.replace(".", "-")


def card(version, day, notes_path):
    title, lede, groups = parse_notes(notes_path)
    tag = f'<span class="tag pixel">v{version}</span>'
    if is_patch(version):
        tag += f' <time class="release-date" datetime="{day.isoformat()}">{nice_date(day)}</time>'
    lines = [
        f'    <article class="release{" patch" if is_patch(version) else ""}" id="{anchor_of(version)}">',
        f'      <h2 class="pixel">{inline(title)} {tag}</h2>',
    ]
    banner = f"img/banner-v{version}.png"
    if not is_patch(version) and os.path.exists(os.path.join(SITE, banner)):
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


def sub_once(pattern, new, text):
    return re.sub(pattern, lambda m: new, text, count=1, flags=re.S)


def landing(version, day, notes_path, has_card):
    """Points the home page's release banner at this release."""
    page = open(INDEX, encoding="utf-8").read()
    found = re.search(r"(<!-- latest-release[^>]*-->\n)(.*?)(    <!-- /latest-release -->)", page, re.S)
    if not found:
        print("index.html has no <!-- latest-release --> markers - home page left alone")
        return
    block = found.group(2)
    link = f"releases.html#{anchor_of(version)}" if has_card else "releases.html"
    block = sub_once(r'href="releases\.html[^"]*"', f'href="{link}"', block)
    block = sub_once(r"New in v[0-9.]+", f"New in v{version}", block)
    block = sub_once(
        r'<time class="rb-date pixel"[^>]*>[^<]*</time>',
        f'<time class="rb-date pixel" datetime="{day.isoformat()}">{nice_date(day)}</time>',
        block,
    )
    if not is_patch(version) and notes_path:
        title, lede, _ = parse_notes(notes_path)
        block = sub_once(r'(?<=<span class="rb-title pixel">)[^<]*', inline(title), block)
        block = sub_once(r'(?<=<span class="rb-sub">)[^<]*', inline(lede), block)
        art = f"img/banner-v{version}-art.webp"
        small = f"img/banner-v{version}-art-960.webp"
        if os.path.exists(os.path.join(SITE, art)):
            if not os.path.exists(os.path.join(SITE, small)):
                small = art
            alt = html.escape(f"New Worlds v{version}: {title}")
            block = sub_once(
                r"<img .*?>",
                f'<img src="{small}"\n'
                f'           srcset="{small} 960w, {art} 1920w"\n'
                f'           sizes="(max-width: 1080px) 100vw, 1048px" width="1920" height="720"\n'
                f'           alt="{alt}">',
                block,
            )
        else:
            print(f"No {art} - the home page banner keeps its old art")
    page = page[: found.start(2)] + block + page[found.end(2) :]
    open(INDEX, "w", encoding="utf-8").write(page)
    print(f"index.html: banner points at v{version}")


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
            f"<td>{nice_date(day)}</td></tr>\n"
        )
        page, rows = re.subn(r"(<!-- versions -->\n)", lambda m: m.group(1) + row, page, count=1)
        if not rows:
            sys.exit("releases.html has no <!-- versions --> marker")

    notes = argv[3] if len(argv) == 4 else None
    if notes:
        new = card(version, day, notes)
        page, replaced = re.subn(
            rf'    <article class="release[^"]*" id="{anchor_of(version)}">.*?</article>\n',
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
    landing(version, day, notes, f'id="{anchor_of(version)}"' in page)


if __name__ == "__main__":
    main(sys.argv)
