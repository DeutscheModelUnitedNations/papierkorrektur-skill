#!/usr/bin/env python3
"""Holt Gremientexte wörtlich von guide.dmun.de (Ghost Content API).

Der Schlüssel ist der öffentliche Suchschlüssel, den jede Guide-Seite im HTML
mitbringt (`data-key`); das Skript liest ihn bei jedem Aufruf frisch aus.

Aufrufe:
  guide.py suche "Klimaflucht"                 Treffer: Titel | Konferenz | URL
  guide.py suche "Klima" --konferenz munbw     nur Themen dieser Guide-Wurzel
  guide.py text <slug-oder-url>                Seite als Klartext (wörtlich)
  guide.py text <slug> --abschnitt "Punkte zur Diskussion"

Nur Standardbibliothek.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://guide.dmun.de"
UA = {"User-Agent": "papierkorrektur-skill"}


def _get(url: str) -> str:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            return r.read().decode("utf-8")
    except urllib.error.URLError as err:
        # z. B. python.org-Python auf macOS ohne Zertifikate: auf curl ausweichen
        try:
            return subprocess.run(["curl", "-fsSL", "-A", UA["User-Agent"], url],
                                  check=True, capture_output=True, text=True, timeout=30).stdout
        except (OSError, subprocess.SubprocessError):
            sys.exit(f"guide.dmun.de nicht erreichbar ({err}) – Browser oder WebFetch nutzen.")


def content_key() -> str:
    m = re.search(r'data-key="([0-9a-f]{20,})"', _get(BASE + "/"))
    if not m:
        sys.exit("Kein Content-Key im HTML von guide.dmun.de gefunden – Browser oder WebFetch nutzen.")
    return m.group(1)


def api(path: str, **params: str) -> dict:
    params["key"] = content_key()
    return json.loads(_get(f"{BASE}/ghost/api/content/{path}?{urllib.parse.urlencode(params)}"))


def to_text(fragment: str) -> str:
    fragment = re.sub(r"<li[^>]*>", "\n- ", fragment)
    fragment = re.sub(r"<(br|/p|/h\d|/li|/ul|/ol|/blockquote|/figure)[^>]*>", "\n", fragment)
    fragment = re.sub(r"<h(\d)[^>]*>", lambda m: "\n" + "#" * int(m.group(1)) + " ", fragment)
    text = html.unescape(re.sub(r"<[^>]+>", "", fragment))
    text = re.sub(r"[ \t]+\n", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def suche(begriff: str, konferenz: str | None) -> int:
    data = api("posts/", limit="all", fields="title,slug,url", include="tags",
               filter=f"title:~'{begriff.replace(chr(39), '')}'")
    treffer = 0
    for p in data.get("posts", []):
        wurzel = urllib.parse.urlparse(p["url"]).path.strip("/").split("/")[0]
        if konferenz and wurzel != konferenz.strip("/"):
            continue
        treffer += 1
        print(f"{p['title'].lstrip('–- ').strip()} | {wurzel} | {p['url']}")
    if not treffer:
        print("Kein Treffer. Kürzeren oder sinngleichen Begriff versuchen.", file=sys.stderr)
        return 1
    return 0


def text(ref: str, abschnitt: str | None) -> int:
    slug = urllib.parse.urlparse(ref).path.strip("/").split("/")[-1] if "/" in ref else ref
    data = api(f"posts/slug/{urllib.parse.quote(slug)}/", formats="html")
    post = data["posts"][0]
    body = to_text(post.get("html") or "")
    if abschnitt:
        i = body.find(abschnitt)
        if i < 0:
            print(f"Abschnitt „{abschnitt}“ nicht gefunden.", file=sys.stderr)
            return 1
        rest = body[i:]
        m = re.search(r"\n#+ ", rest[len(abschnitt):])
        body = rest[: len(abschnitt) + m.start()] if m else rest
    print(f"# {post['title'].lstrip('–- ').strip()}\n{post['url']}\n\n{body}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("suche")
    s.add_argument("begriff")
    s.add_argument("--konferenz", help="Guide-Wurzel, z. B. munbw oder mun-sh")
    t = sub.add_parser("text")
    t.add_argument("ref", help="Slug oder URL der Themenseite")
    t.add_argument("--abschnitt", help="nur diesen Abschnitt ausgeben")
    a = ap.parse_args()
    return suche(a.begriff, a.konferenz) if a.cmd == "suche" else text(a.ref, a.abschnitt)


if __name__ == "__main__":
    sys.exit(main())
