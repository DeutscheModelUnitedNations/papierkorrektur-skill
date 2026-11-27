#!/usr/bin/env python3
"""Setzt die Versionsnummer an allen Stellen, an denen sie im Repo steht.

- .claude-plugin/marketplace.json: `metadata.version` und `version` jedes Plugins mit lokaler Quelle
- <plugin>/.claude-plugin/plugin.json: `version`

Aufruf:
    python3 scripts/bump_version.py patch|minor|major   # von der aktuellen Version aus hochzählen
    python3 scripts/bump_version.py 1.2.3               # feste Version setzen (muss größer sein)
    python3 scripts/bump_version.py --current            # nur aktuelle Version ausgeben

Gibt die neue Version auf stdout aus. Nur Standardbibliothek.
Ausgangspunkt ist `metadata.version`; weichen die Stellen voneinander ab, bricht das Skript ab
(dann erst `scripts/lint_skill.py` grün machen).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
STUFEN = ("patch", "minor", "major")


class Fehler(Exception):
    pass


def parse(version: str) -> tuple[int, int, int]:
    m = VERSION_RE.match(version or "")
    if not m:
        raise Fehler(f"keine Version im Format X.Y.Z: {version!r}")
    return int(m[1]), int(m[2]), int(m[3])


def naechste(aktuell: str, ziel: str) -> str:
    major, minor, patch = parse(aktuell)
    if ziel == "major":
        return f"{major + 1}.0.0"
    if ziel == "minor":
        return f"{major}.{minor + 1}.0"
    if ziel == "patch":
        return f"{major}.{minor}.{patch + 1}"
    ziel = ziel.removeprefix("v")
    if parse(ziel) <= parse(aktuell):
        raise Fehler(f"neue Version {ziel} ist nicht größer als {aktuell}")
    return ziel


def lade(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def schreibe(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def dateien(root: Path) -> tuple[Path, dict, list[tuple[Path, dict]]]:
    market_path = root / ".claude-plugin" / "marketplace.json"
    market = lade(market_path)
    manifeste = []
    for entry in market.get("plugins", []):
        source = entry.get("source")
        if isinstance(source, str):
            p = (root / source / ".claude-plugin" / "plugin.json").resolve()
            manifeste.append((p, lade(p)))
    return market_path, market, manifeste


def aktuelle_version(root: Path) -> str:
    _, market, manifeste = dateien(root)
    gefunden = {market.get("metadata", {}).get("version")}
    gefunden |= {e.get("version") for e in market.get("plugins", []) if isinstance(e.get("source"), str)}
    gefunden |= {m.get("version") for _, m in manifeste}
    gefunden.discard(None)
    if len(gefunden) != 1:
        raise Fehler(f"Versionsnummern weichen ab oder fehlen: {sorted(gefunden)}")
    return gefunden.pop()


def setze(root: Path, neu: str) -> None:
    market_path, market, manifeste = dateien(root)
    market.setdefault("metadata", {})["version"] = neu
    for entry in market.get("plugins", []):
        if isinstance(entry.get("source"), str):
            entry["version"] = neu
    schreibe(market_path, market)
    for path, manifest in manifeste:
        manifest["version"] = neu
        schreibe(path, manifest)


def main(argv: list[str], root: Path = ROOT) -> int:
    if len(argv) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        aktuell = aktuelle_version(root)
        if argv[0] == "--current":
            print(aktuell)
            return 0
        neu = naechste(aktuell, argv[0])
        setze(root, neu)
    except Fehler as e:
        print(f"Fehler: {e}", file=sys.stderr)
        return 1
    print(neu)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
