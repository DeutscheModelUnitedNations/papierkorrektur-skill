#!/usr/bin/env python3
"""Prüft Marketplace, Plugins und Skills dieses Repos auf Fehler, die `claude plugin validate` nicht sieht.

- Versionsnummern: marketplace.json (metadata + Plugin-Eintrag) und plugin.json stimmen überein
- Marketplace-Quellen zeigen auf vorhandene Plugin-Ordner
- SKILL.md-Frontmatter: `name` passt zum Ordner, Format, `description` vorhanden und ≤ 1024 Zeichen
- Relative Verweise in allen Markdown-Dateien eines Skills zeigen auf vorhandene Dateien
  (Markdown-Links und Code-Spans wie `references/x.md` oder `<skill-ordner>/scripts/y.py`)

- Mit `--tag vX.Y.Z` (CI bei Tag-Push): der Tag passt zur Versionsnummer in den Dateien

Aufruf: python3 scripts/lint_skill.py [--tag vX.Y.Z] [repo-wurzel]
Nur Standardbibliothek. Exit-Code 1 bei Fehlern.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DESCRIPTION_LIMIT = 1024
DESCRIPTION_WARN = 950
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
CODE_PATH_RE = re.compile(r"`(?:<skill-ordner>/)?((?:references|scripts|assets)/[^`\s]+)`")

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        err(f"{path}: nicht lesbar ({e})")
        return {}


def frontmatter(path: Path) -> dict[str, str] | None:
    """Liest einfaches YAML-Frontmatter (key: value, einzeilig)."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.startswith((" ", "\t", "#")):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            err(f"{path}: Frontmatter-Zeile ohne Doppelpunkt: {line!r}")
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        fields[key.strip()] = value
    return fields


def check_skill(skill_dir: Path, root: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    rel = skill_md.relative_to(root)
    if not skill_md.is_file():
        err(f"{skill_dir.relative_to(root)}: SKILL.md fehlt")
        return
    fm = frontmatter(skill_md)
    if fm is None:
        err(f"{rel}: kein Frontmatter (--- … ---) am Dateianfang")
        return
    name = fm.get("name", "")
    if not name:
        err(f"{rel}: `name` fehlt im Frontmatter")
    else:
        if name != skill_dir.name:
            err(f"{rel}: `name` ({name}) passt nicht zum Ordnernamen ({skill_dir.name})")
        if len(name) > 64 or not NAME_RE.match(name):
            err(f"{rel}: `name` ({name}) muss aus a–z, 0–9 und Bindestrichen bestehen, ≤ 64 Zeichen")
    desc = fm.get("description", "")
    if not desc:
        err(f"{rel}: `description` fehlt im Frontmatter")
    else:
        n = len(desc)
        if n > DESCRIPTION_LIMIT:
            err(f"{rel}: `description` hat {n} Zeichen, erlaubt sind {DESCRIPTION_LIMIT}")
        elif n > DESCRIPTION_WARN:
            warn(f"{rel}: `description` hat {n} von {DESCRIPTION_LIMIT} Zeichen")
        if re.search(r"<[a-zA-Z/][^>]*>", desc):
            err(f"{rel}: `description` enthält XML-/HTML-Tags")

    for md in sorted(skill_dir.rglob("*.md")):
        check_links(md, skill_dir, root)


def check_links(md: Path, skill_dir: Path, root: Path) -> None:
    text = md.read_text(encoding="utf-8")
    # Codeblöcke für Markdown-Links ausblenden; Code-Spans werden separat geprüft.
    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    rel = md.relative_to(root)
    for target in LINK_RE.findall(prose):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith(("#", "<")):
            continue  # URL, mailto:, Anker, Platzhalter wie <Deeplink>
        path = target.split("#", 1)[0]
        if path and not (md.parent / path).exists():
            err(f"{rel}: Link auf fehlende Datei: {target}")
    for target in CODE_PATH_RE.findall(text):
        path = target.split("#", 1)[0].rstrip(".,;:")
        if "<" in path or "*" in path:
            continue  # Platzhalter
        if not ((skill_dir / path).exists() or (md.parent / path).exists()):
            err(f"{rel}: Verweis auf fehlende Datei: {target}")


def main() -> int:
    args = sys.argv[1:]
    tag = None
    if "--tag" in args:
        i = args.index("--tag")
        if i + 1 >= len(args):
            print("Fehler: --tag braucht einen Wert, z. B. --tag v1.2.3")
            return 2
        tag = args[i + 1]
        del args[i:i + 2]
    root = Path(args[0] if args else Path(__file__).resolve().parent.parent).resolve()
    market_path = root / ".claude-plugin" / "marketplace.json"
    market = load_json(market_path)
    market_version = market.get("metadata", {}).get("version")
    if tag is not None and tag != f"v{market_version}":
        err(f"Tag {tag} passt nicht zur Version in marketplace.json ({market_version}), erwartet v{market_version}")

    for entry in market.get("plugins", []):
        pname = entry.get("name", "?")
        source = entry.get("source")
        if not isinstance(source, str):
            continue  # externe Quelle (GitHub, URL): hier nicht prüfbar
        plugin_dir = (root / source).resolve()
        if not plugin_dir.is_dir():
            err(f"marketplace.json: Quelle von {pname} ({source}) ist kein Ordner")
            continue
        manifest = load_json(plugin_dir / ".claude-plugin" / "plugin.json")
        versions = {
            "marketplace.json metadata.version": market_version,
            f"marketplace.json plugins[{pname}].version": entry.get("version"),
            f"{(plugin_dir / '.claude-plugin' / 'plugin.json').relative_to(root)} version": manifest.get("version"),
        }
        present = {k: v for k, v in versions.items() if v is not None}
        if len(set(present.values())) > 1:
            err("Versionsnummern weichen ab:\n" + "\n".join(f"    {k}: {v}" for k, v in present.items()))
        if manifest.get("name") and manifest["name"] != pname:
            err(f"marketplace.json: Plugin heißt {pname}, plugin.json sagt {manifest['name']}")
        skills_root = plugin_dir / "skills"
        if skills_root.is_dir():
            for skill_dir in sorted(p for p in skills_root.iterdir() if p.is_dir()):
                check_skill(skill_dir, root)

    for w in warnings:
        print(f"Warnung: {w}")
    for e in errors:
        print(f"Fehler: {e}")
    if errors:
        print(f"\n{len(errors)} Fehler.")
        return 1
    print("Skill-Lint ok.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
