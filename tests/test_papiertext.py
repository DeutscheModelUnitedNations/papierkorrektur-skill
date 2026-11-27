"""Rauchtests für plugins/papierkorrektur/skills/papierkorrektur/scripts/papiertext.py.

Die Fixtures sind von Hand gebaut, nach dem Format, das papiertext.py erwartet (TipTap-JSON für
Positionspapiere, Resolutions-JSON für Arbeitspapiere, GraphQL-Antwort mit `versions`). Ändert
der DELEGATOR sein Format, gehört ein echtes (anonymisiertes) Beispiel hierher.

Aufruf: python3 -m unittest discover -s tests -v
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "plugins/papierkorrektur/skills/papierkorrektur/scripts/papiertext.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

spec = importlib.util.spec_from_file_location("papiertext", SCRIPT)
pt = importlib.util.module_from_spec(spec)
sys.modules["papiertext"] = pt  # dataclasses brauchen das Modul in sys.modules
spec.loader.exec_module(pt)


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def run(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], input=stdin,
                          capture_output=True, text=True, cwd=FIXTURES)


class Base(unittest.TestCase):
    def setUp(self) -> None:
        pt.META.clear()


class Positionspapier(Base):
    def test_abschnitte_und_wortzahlen(self):
        versions = pt.find_versions(fixture("positionspapier.json"))
        self.assertEqual(list(versions), [0])
        kind, sections = pt.to_sections(versions[0])
        self.assertEqual(kind, "Positionspapier")
        self.assertEqual([s.title for s in sections], ["Hintergrund", "Position", "Zusammenfassung"])
        self.assertEqual(sections[0].question, "Hintergrund: Wie ist die Lage in Ihrem Land?")
        self.assertEqual([s.words for s in sections], [150, 93, 100])

    def test_verschachtelte_listen(self):
        _, sections = pt.to_sections(pt.find_versions(fixture("positionspapier.json"))[0])
        lines = sections[1].paragraphs
        self.assertTrue(lines[0].startswith("- Erstens"))
        self.assertTrue(lines[1].startswith("- Zweitens"))
        self.assertTrue(lines[2].startswith("    1. Unterpunkt"))

    def test_formalpruefung(self):
        _, sections = pt.to_sections(pt.find_versions(fixture("positionspapier.json"))[0])
        checks = pt.formal_checks("Positionspapier", sections, sum(s.words for s in sections))
        self.assertTrue(all(ok for ok, _ in checks), checks)

    def test_zu_lange_zusammenfassung(self):
        doc = json.loads(fixture("positionspapier.json"))
        summary_item = doc["content"][0]["content"][2]
        summary_item["content"][1]["content"][0]["text"] = " ".join(["Wort"] * 160)
        _, sections = pt.to_sections(doc)
        total = sum(s.words for s in sections)
        failed = [text for ok, text in pt.formal_checks("Positionspapier", sections, total) if not ok]
        self.assertEqual(failed, ["Zusammenfassung ≤ 150 Wörter (ist: 160)"])

    def test_content_als_json_string(self):
        doubly_encoded = json.dumps(json.dumps(json.loads(fixture("positionspapier.json"))))
        self.assertEqual(list(pt.find_versions(doubly_encoded)), [0])


class Arbeitspapier(Base):
    def setUp(self) -> None:
        super().setUp()
        kind, self.sections = pt.to_sections(pt.find_versions(fixture("arbeitspapier.json"))[0])
        self.assertEqual(kind, "Arbeitspapier")
        self.pre, self.op = self.sections

    def test_praeambel(self):
        self.assertEqual(self.pre.paragraphs[0], "P1. in Anbetracht der Lage")
        self.assertEqual(len(self.pre.paragraphs), 3)

    def test_unterpunkte_neues_format(self):
        self.assertEqual(self.op.paragraphs[0].split("\n"), [
            "1. fordert alle Staaten auf,",
            "    a) Programme zu fördern",
            "    b) Mittel bereitzustellen",
            "        i. insbesondere für Bildung",
        ])

    def test_unterpunkte_altformat(self):
        self.assertEqual(self.op.paragraphs[2].split("\n"), [
            "3. ermutigt die Mitgliedstaaten",
            "    a) regional zu kooperieren",
            "        i. über Grenzen hinweg",
        ])

    def test_formalpruefung(self):
        checks = dict((text, ok) for ok, text in
                      pt.formal_checks("Arbeitspapier", self.sections, sum(s.words for s in self.sections)))
        self.assertTrue(checks["Präambel ≥ 3 Absätze (ist: 3)"])
        self.assertFalse(checks["Operativer Teil ≥ 5 Absätze (ist: 4)"])
        self.assertFalse(checks["Alle Absätze beginnen klein (groß: P3)"])


class Versionen(Base):
    def test_zweitkorrektur(self):
        out = run("antwort_zweitkorrektur.json")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("<!-- Version 3 von [1, 2, 3] -->", out.stdout)
        self.assertIn("Zweitkorrektur: zuletzt bewertet wurde Version 2.", out.stdout)

    def test_diff_gegen_bewertete_version(self):
        out = run("antwort_zweitkorrektur.json", "--diff")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("# Änderungen Version 2 → 3", out.stdout)
        self.assertIn("| Hintergrund | 150 | 160 | leicht geändert", out.stdout)
        self.assertIn("| Position | 93 | 93 | unverändert", out.stdout)
        self.assertIn("+ jetzt:", out.stdout)

    def test_diff_mit_gegen(self):
        out = run("antwort_zweitkorrektur.json", "--diff", "--version", "2", "--gegen", "1")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("textgleich mit Version 1", out.stdout)

    def test_erstkorrektur(self):
        out = run("antwort_erstkorrektur.json")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("> Erstkorrektur", out.stdout)
        self.assertIn("Version 2 ist textgleich mit Version 1.", out.stdout)
        diff = run("antwort_erstkorrektur.json", "--diff")
        self.assertEqual(diff.returncode, 0, diff.stderr)
        self.assertIn("Keine bewertete Vorversion", diff.stdout)

    def test_unbekannte_version(self):
        out = run("antwort_zweitkorrektur.json", "--version", "9")
        self.assertEqual(out.returncode, 1)
        self.assertIn("Version 9 nicht in der Eingabe", out.stderr)


class Eingaben(Base):
    def test_klartext(self):
        out = run("--text", stdin="Ein kurzer Absatz.\n\nNoch ein Absatz mit fünf Wörtern.")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("Klartext: 9 Wörter in 2 Absätzen.", out.stdout)

    def test_json_ohne_papier(self):
        out = run("-", stdin='{"data": {"paper": null}}')
        self.assertEqual(out.returncode, 1)
        self.assertIn("Kein Papierinhalt gefunden", out.stderr)


if __name__ == "__main__":
    unittest.main()
