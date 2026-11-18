#!/usr/bin/env python3
"""Wandelt TipTap-JSON aus dem MUNIFY DELEGATOR in Markdown um und zählt Wörter.

Eingabe (Datei oder stdin):
  - das rohe `content` einer Paperversion (JSON-Objekt oder JSON-String), oder
  - eine ganze GraphQL-Antwort; dann wird die erste `content`-Eigenschaft
    mit TipTap-Dokument verwendet.

Ausgabe: Markdown des Papiers, danach eine Tabelle mit Wortzahlen je Abschnitt.
Nur Standardbibliothek.
"""
from __future__ import annotations

import json
import re
import sys
from typing import Any

SUMMARY_LIMIT = 150


def _load(raw: str) -> Any:
    data: Any = json.loads(raw)
    while isinstance(data, str):
        data = json.loads(data)
    return data


def _find_doc(node: Any) -> dict | None:
    if isinstance(node, dict):
        if node.get("type") == "doc":
            return node
        for key, value in node.items():
            if key == "content" and isinstance(value, str):
                try:
                    found = _find_doc(_load(value))
                except (json.JSONDecodeError, TypeError):
                    found = None
            else:
                found = _find_doc(value)
            if found:
                return found
    elif isinstance(node, list):
        for item in node:
            found = _find_doc(item)
            if found:
                return found
    return None


def _inline(node: dict) -> str:
    out = []
    for child in node.get("content", []) or []:
        if child.get("type") == "text":
            text = child.get("text", "")
            marks = {m.get("type") for m in child.get("marks", []) or []}
            if "bold" in marks:
                text = f"**{text}**"
            if "italic" in marks:
                text = f"*{text}*"
            out.append(text)
        elif child.get("type") == "hardBreak":
            out.append("\n")
        else:
            out.append(_inline(child))
    return "".join(out).strip()


def _words(text: str) -> int:
    return len(re.findall(r"\w[\w'’-]*", text))


def convert(doc: dict) -> tuple[str, list[tuple[str, int]]]:
    """Gibt Markdown und (Abschnitt, Wortzahl) zurück.

    Ein Abschnitt ist ein Listenpunkt der obersten nummerierten Liste; sein erster
    Absatz ist die Leitfrage, der Rest die Antwort. Absätze nach der Liste werden
    dem letzten Abschnitt zugerechnet (häufig die Zusammenfassung).
    """
    lines: list[str] = []
    sections: list[list] = []  # [titel, wortzahl]

    def add_text(text: str) -> None:
        if not text:
            return
        lines.append(text + "\n")
        if sections:
            sections[-1][1] += _words(text)

    for block in doc.get("content", []) or []:
        btype = block.get("type")
        if btype in ("orderedList", "bulletList"):
            for i, item in enumerate(block.get("content", []) or [], start=1):
                paras = item.get("content", []) or []
                question = _inline(paras[0]) if paras else ""
                title = question.split(":", 1)[0].strip() or f"Abschnitt {i}"
                sections.append([title, 0])
                lines.append(f"## {i}. {title}\n")
                lines.append(f"> {question}\n")
                for para in paras[1:]:
                    add_text(_inline(para))
        elif btype == "heading":
            level = (block.get("attrs") or {}).get("level", 2)
            title = _inline(block)
            sections.append([title, 0])
            lines.append(f"{'#' * level} {title}\n")
        else:
            add_text(_inline(block))

    return "\n".join(lines), [(t, n) for t, n in sections]


def main() -> int:
    raw = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    doc = _find_doc(_load(raw))
    if not doc:
        print("Kein TipTap-Dokument gefunden.", file=sys.stderr)
        return 1
    markdown, sections = convert(doc)
    print(markdown)
    print("---\n\n| Abschnitt | Wörter |\n|---|---|")
    for title, count in sections:
        flag = ""
        if title.lower().startswith("zusammenfassung") and count > SUMMARY_LIMIT:
            flag = f" ⚠ über {SUMMARY_LIMIT}"
        elif count == 0:
            flag = " ⚠ leer"
        print(f"| {title} | {count}{flag} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
