#!/usr/bin/env python3
"""Macht Papiere aus dem MUNIFY DELEGATOR lesbar und vergleicht Versionen.

Eingabe (Datei oder stdin): eine GraphQL-Antwort mit `versions { version content }`
oder das rohe `content` einer Version. Unterstützt:
  - Positionspapiere: TipTap-JSON (`{"type":"doc", ...}`)
  - Arbeitspapiere: Resolutions-JSON (`preamble` + `operative`, auch das Altformat)

Aufrufe:
  papiertext.py antwort.json               neueste Version als Markdown + Wortzahlen
  papiertext.py antwort.json --version 2   eine bestimmte Version
  papiertext.py antwort.json --diff        Änderungen neueste vs. vorherige Version
  papiertext.py antwort.json --diff --version 3 --gegen 1

Der ausgegebene Text ist wörtlich (ohne Formatierungszeichen), damit Zitate im
DELEGATOR über „Im Papier finden“ wiedergefunden werden.
Nur Standardbibliothek.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import string
import sys
from dataclasses import dataclass, field
from typing import Any

SUMMARY_LIMIT = 150


# --------------------------------------------------------------------------- Laden

def _parse(value: Any) -> Any:
    while isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _is_tiptap(obj: Any) -> bool:
    return isinstance(obj, dict) and obj.get("type") == "doc"


def _is_resolution(obj: Any) -> bool:
    return isinstance(obj, dict) and isinstance(obj.get("preamble"), list) and isinstance(obj.get("operative"), list)


def find_versions(data: Any) -> dict[int, Any]:
    """Sammelt {versionsnummer: inhalt}. Rohes Dokument → Version 0."""
    data = _parse(data)
    if _is_tiptap(data) or _is_resolution(data):
        return {0: data}
    found: dict[int, Any] = {}

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if "content" in node and "version" in node:
                content = _parse(node["content"])
                if _is_tiptap(content) or _is_resolution(content):
                    found[int(node["version"])] = content
            for value in node.values():
                if isinstance(value, (dict, list)):
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    if not found:
        # Ein `content` ohne `version` (z. B. nur das Feld abgefragt)
        def first_content(node: Any) -> Any:
            if isinstance(node, dict):
                if "content" in node:
                    c = _parse(node["content"])
                    if _is_tiptap(c) or _is_resolution(c):
                        return c
                for v in node.values():
                    r = first_content(v)
                    if r is not None:
                        return r
            elif isinstance(node, list):
                for v in node:
                    r = first_content(v)
                    if r is not None:
                        return r
            return None

        c = first_content(data)
        if c is not None:
            found[0] = c
    return found


# --------------------------------------------------------------------------- Modell

@dataclass
class Section:
    title: str
    question: str = ""
    paragraphs: list[str] = field(default_factory=list)

    @property
    def words(self) -> int:
        return sum(_words(p) for p in self.paragraphs)


def _words(text: str) -> int:
    return len(re.findall(r"\w[\w'’-]*", text))


def _inline(node: dict) -> str:
    out = []
    for child in node.get("content", []) or []:
        ctype = child.get("type")
        if ctype == "text":
            out.append(child.get("text", ""))
        elif ctype == "hardBreak":
            out.append("\n")
        else:
            out.append(_inline(child))
    return "".join(out).strip()


def _list_lines(node: dict, depth: int = 0) -> list[str]:
    lines = []
    ordered = node.get("type") == "orderedList"
    for i, item in enumerate(node.get("content", []) or [], start=1):
        prefix = f"{i}." if ordered else "-"
        first = True
        for child in item.get("content", []) or []:
            if child.get("type") in ("orderedList", "bulletList"):
                lines.extend(_list_lines(child, depth + 1))
            else:
                text = _inline(child)
                if text:
                    lines.append(("    " * depth) + (f"{prefix} " if first else "  ") + text)
                    first = False
    return lines


def sections_from_tiptap(doc: dict) -> list[Section]:
    """Positionspapier: die oberste nummerierte Liste gibt die Abschnitte vor.

    Erster Absatz eines Listenpunkts = Leitfrage, Rest = Antwort. Absätze nach der
    Liste gehören zum letzten Abschnitt (häufig rutscht die Zusammenfassung dorthin).
    """
    sections: list[Section] = []
    preface = Section("Vor den Abschnitten")

    def target() -> Section:
        return sections[-1] if sections else preface

    for block in doc.get("content", []) or []:
        btype = block.get("type")
        if btype == "orderedList" and not sections:
            for i, item in enumerate(block.get("content", []) or [], start=1):
                paras = item.get("content", []) or []
                question = _inline(paras[0]) if paras else ""
                title = question.split(":", 1)[0].strip() or f"Abschnitt {i}"
                sec = Section(title, question)
                for para in paras[1:]:
                    if para.get("type") in ("orderedList", "bulletList"):
                        sec.paragraphs.extend(_list_lines(para))
                    else:
                        text = _inline(para)
                        if text:
                            sec.paragraphs.append(text)
                sections.append(sec)
        elif btype == "heading":
            sections.append(Section(_inline(block)))
        elif btype in ("orderedList", "bulletList"):
            target().paragraphs.extend(_list_lines(block))
        else:
            text = _inline(block)
            if text:
                target().paragraphs.append(text)
    if not sections:
        preface.title = "Fließtext"
    return ([preface] if preface.paragraphs else []) + sections


_LETTERS = string.ascii_lowercase


def _roman(n: int) -> str:
    vals = [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out


def _label(depth: int, i: int) -> str:
    if depth == 1:
        return f"{_LETTERS[(i - 1) % 26]})"
    if depth == 2:
        return f"{_roman(i)}."
    return f"{i}."


def _blocks_lines(blocks: list, depth: int) -> list[str]:
    lines = []
    for block in blocks or []:
        if block.get("type") == "text":
            lines.append(block.get("content", "").strip())
        elif block.get("type") == "subclauses":
            for j, sub in enumerate(block.get("items", []) or [], start=1):
                sub_lines = _blocks_lines(sub.get("blocks", []), depth + 1)
                if sub_lines:
                    sub_lines[0] = ("    " * (depth + 1)) + _label(depth + 1, j) + " " + sub_lines[0].lstrip()
                    lines.extend(sub_lines)
    return lines


def _legacy_lines(subs: list, depth: int) -> list[str]:
    lines = []
    for j, sub in enumerate(subs or [], start=1):
        lines.append(("    " * (depth + 1)) + _label(depth + 1, j) + " " + sub.get("content", "").strip())
        lines.extend(_legacy_lines(sub.get("children", []), depth + 1))
    return lines


def sections_from_resolution(res: dict) -> list[Section]:
    pre = Section("Präambel")
    for i, clause in enumerate(res.get("preamble", []) or [], start=1):
        pre.paragraphs.append(f"P{i}. {clause.get('content', '').strip()}")
    op = Section("Operativer Teil")
    for i, clause in enumerate(res.get("operative", []) or [], start=1):
        if "blocks" in clause:
            lines = _blocks_lines(clause.get("blocks", []), 0)
        else:  # Altformat
            lines = [clause.get("content", "").strip()] + _legacy_lines(clause.get("subClauses", []), 0)
        if lines:
            lines[0] = f"{i}. {lines[0]}"
            op.paragraphs.append("\n".join(lines))
    return [pre, op]


def to_sections(content: Any) -> tuple[str, list[Section]]:
    if _is_resolution(content):
        return "Arbeitspapier", sections_from_resolution(content)
    return "Positionspapier", sections_from_tiptap(content)


# --------------------------------------------------------------------------- Ausgabe

def render(kind: str, sections: list[Section], committee: str | None = None) -> str:
    out = []
    for sec in sections:
        out.append(f"## {sec.title}\n")
        if sec.question:
            out.append(f"> {sec.question}\n")
        for para in sec.paragraphs:
            out.append(para + "\n")
    out.append("---\n")
    out.append("| Abschnitt | Wörter | Hinweis |\n|---|---|---|")
    for sec in sections:
        hint = ""
        if sec.title.lower().startswith("zusammenfassung") and sec.words > SUMMARY_LIMIT:
            hint = f"über {SUMMARY_LIMIT}"
        elif sec.words == 0:
            hint = "leer"
        if kind == "Arbeitspapier":
            hint = (hint + "; " if hint else "") + f"{len(sec.paragraphs)} Absätze"
        out.append(f"| {sec.title} | {sec.words} | {hint} |")
    total = sum(s.words for s in sections)
    out.append(f"\n{kind}, insgesamt {total} Wörter.")
    checks = formal_checks(kind, sections, total)
    if checks:
        out.append("\n### Formalprüfung (automatisch)\n")
        out.extend(f"- {'✓' if ok else '✗'} {text}" for ok, text in checks)
    return "\n".join(out)


def _first_line(paragraph: str) -> str:
    return re.sub(r"^(P?\d+\.)\s*", "", paragraph.split("\n")[0]).strip()


def _last_line(paragraph: str) -> str:
    return paragraph.split("\n")[-1].strip()


def formal_checks(kind: str, sections: list[Section], total: int) -> list[tuple[bool, str]]:
    """Mechanisch prüfbare Punkte aus dem Korrekturleitfaden."""
    if kind == "Positionspapier":
        checks = [(300 <= total <= 500, f"Länge 300–500 Wörter (ist: {total})")]
        for sec in sections:
            if sec.title.lower().startswith("zusammenfassung"):
                checks.append((sec.words <= SUMMARY_LIMIT, f"Zusammenfassung ≤ {SUMMARY_LIMIT} Wörter (ist: {sec.words})"))
        return checks
    pre = next((s for s in sections if s.title == "Präambel"), Section(""))
    op = next((s for s in sections if s.title == "Operativer Teil"), Section(""))
    checks = [
        (len(pre.paragraphs) >= 3, f"Präambel ≥ 3 Absätze (ist: {len(pre.paragraphs)})"),
        (len(op.paragraphs) >= 5, f"Operativer Teil ≥ 5 Absätze (ist: {len(op.paragraphs)})"),
    ]
    def bad(paras, test):
        return [i for i, p in enumerate(paras, start=1) if not test(p)]
    up = bad(pre.paragraphs + op.paragraphs, lambda p: not _first_line(p)[:1].isupper())
    checks.append((not up, "Alle Absätze beginnen klein" + (f" (groß: {', '.join(_nr(i, len(pre.paragraphs)) for i in up)})" if up else "")))
    pc = bad(pre.paragraphs, lambda p: _last_line(p).endswith(","))
    checks.append((not pc, "Präambelabsätze enden mit Komma" + (f" (nicht: P{', P'.join(map(str, pc))})" if pc else "")))
    body, last = op.paragraphs[:-1], op.paragraphs[-1:]
    sc = bad(body, lambda p: _last_line(p).endswith(";"))
    checks.append((not sc, "Operative Absätze enden mit Semikolon (außer dem letzten)" + (f" (nicht: {', '.join(map(str, sc))})" if sc else "")))
    if last:
        checks.append((_last_line(last[0]).endswith("."), "Letzter operativer Absatz endet mit Punkt"))
    return checks


def _nr(i: int, n_pre: int) -> str:
    return f"P{i}" if i <= n_pre else str(i - n_pre)


def _ratio(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def render_diff(old: list[Section], new: list[Section], v_old: int, v_new: int) -> str:
    out = [f"# Änderungen Version {v_old} → {v_new}\n",
           "| Abschnitt | Wörter vorher | Wörter jetzt | Änderung |", "|---|---|---|---|"]
    old_by = {s.title: s for s in old}
    new_by = {s.title: s for s in new}
    for title in list(dict.fromkeys([s.title for s in new] + [s.title for s in old])):
        o, n = old_by.get(title), new_by.get(title)
        if o and not n:
            out.append(f"| {title} | {o.words} | – | gestrichen |")
        elif n and not o:
            out.append(f"| {title} | – | {n.words} | neu |")
        else:
            r = _ratio("\n".join(o.paragraphs), "\n".join(n.paragraphs))
            kept = all(p in n.paragraphs for p in o.paragraphs)
            if r == 1:
                label = "unverändert"
            elif kept:
                label = f"ergänzt (+{len(n.paragraphs) - len(o.paragraphs)} Absätze)"
            else:
                label = "leicht geändert" if r > 0.9 else "überarbeitet" if r > 0.5 else "neu geschrieben"
            out.append(f"| {title} | {o.words} | {n.words} | {label}, {r:.0%} gleich |")

    out.append("\n## Geänderte Absätze\n")
    for title in [s.title for s in new]:
        o, n = old_by.get(title), new_by.get(title)
        if not o:
            continue
        sm = difflib.SequenceMatcher(None, o.paragraphs, n.paragraphs)
        changes = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            for p in o.paragraphs[i1:i2]:
                changes.append(f"- vorher: {p[:300]}")
            for p in n.paragraphs[j1:j2]:
                changes.append(f"+ jetzt: {p[:300]}")
        if changes:
            out.append(f"### {title}\n")
            out.extend(changes)
            out.append("")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("datei", nargs="?", help="GraphQL-Antwort oder rohes content (sonst stdin)")
    ap.add_argument("--version", type=int, help="Version (Standard: neueste)")
    ap.add_argument("--diff", action="store_true", help="Änderungen gegenüber einer älteren Version")
    ap.add_argument("--gegen", type=int, help="Vergleichsversion für --diff (Standard: die davor)")
    args = ap.parse_args()

    raw = open(args.datei, encoding="utf-8").read() if args.datei else sys.stdin.read()
    versions = find_versions(raw)
    if not versions:
        print("Kein Papierinhalt gefunden (weder TipTap- noch Resolutions-JSON).", file=sys.stderr)
        return 1
    numbers = sorted(versions)
    v_new = args.version if args.version is not None else numbers[-1]
    if v_new not in versions:
        print(f"Version {v_new} nicht in der Eingabe. Vorhanden: {numbers}", file=sys.stderr)
        return 1
    kind, new_sections = to_sections(versions[v_new])

    if not args.diff:
        print(f"<!-- Version {v_new} von {numbers} -->\n")
        print(render(kind, new_sections))
        return 0

    older = [n for n in numbers if n < v_new]
    v_old = args.gegen if args.gegen is not None else (older[-1] if older else None)
    if v_old is None or v_old not in versions:
        print(f"Keine Vergleichsversion. Vorhanden: {numbers} – Versionen mit abfragen.", file=sys.stderr)
        return 1
    _, old_sections = to_sections(versions[v_old])
    print(render_diff(old_sections, new_sections, v_old, v_new))
    return 0


if __name__ == "__main__":
    sys.exit(main())
