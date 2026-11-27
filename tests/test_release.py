"""Tests für scripts/bump_version.py und den Tag-Check in scripts/lint_skill.py.

Arbeitet auf einer Kopie der beiden Manifeste in einem Temp-Ordner, das Repo bleibt unberührt.

Aufruf: python3 -m unittest discover -s tests -v
"""
from __future__ import annotations

import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUMP = ROOT / "scripts/bump_version.py"
LINT = ROOT / "scripts/lint_skill.py"
MARKET = ".claude-plugin/marketplace.json"
PLUGIN = "plugins/papierkorrektur/.claude-plugin/plugin.json"

spec = importlib.util.spec_from_file_location("bump_version", BUMP)
bv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bv)


class NaechsteVersion(unittest.TestCase):
    def test_stufen(self):
        self.assertEqual(bv.naechste("0.7.3", "patch"), "0.7.4")
        self.assertEqual(bv.naechste("0.7.3", "minor"), "0.8.0")
        self.assertEqual(bv.naechste("0.7.3", "major"), "1.0.0")

    def test_feste_version(self):
        self.assertEqual(bv.naechste("0.7.0", "0.10.0"), "0.10.0")
        self.assertEqual(bv.naechste("0.7.0", "v1.0.0"), "1.0.0")

    def test_feste_version_muss_groesser_sein(self):
        for ziel in ("0.7.0", "0.6.9", "0.10"):
            with self.assertRaises(bv.Fehler, msg=ziel):
                bv.naechste("0.7.0", ziel)


class Kopie(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        for rel in (MARKET, PLUGIN):
            (self.tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / rel, self.tmp / rel)
        self.start = bv.aktuelle_version(self.tmp)

    def run_bump(self, *args: str) -> tuple[int, str]:
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            code = bv.main(list(args), root=self.tmp)
        return code, out.getvalue().strip()

    def versionen(self) -> list[str]:
        market = json.loads((self.tmp / MARKET).read_text(encoding="utf-8"))
        plugin = json.loads((self.tmp / PLUGIN).read_text(encoding="utf-8"))
        return [market["metadata"]["version"], market["plugins"][0]["version"], plugin["version"]]


class Bump(Kopie):
    def test_setzt_alle_stellen(self):
        code, neu = self.run_bump("patch")
        self.assertEqual(code, 0)
        self.assertEqual(neu, bv.naechste(self.start, "patch"))
        self.assertEqual(self.versionen(), [neu] * 3)

    def test_nur_version_aendert_sich(self):
        vorher = {rel: (self.tmp / rel).read_text(encoding="utf-8") for rel in (MARKET, PLUGIN)}
        _, neu = self.run_bump("minor")
        for rel, text in vorher.items():
            self.assertEqual(
                (self.tmp / rel).read_text(encoding="utf-8"),
                text.replace(f'"version": "{self.start}"', f'"version": "{neu}"'),
                rel,
            )

    def test_abweichende_versionen(self):
        path = self.tmp / PLUGIN
        data = json.loads(path.read_text(encoding="utf-8"))
        data["version"] = "9.9.9"
        path.write_text(json.dumps(data), encoding="utf-8")
        code, _ = self.run_bump("patch")
        self.assertEqual(code, 1)

    def test_current(self):
        self.assertEqual(self.run_bump("--current"), (0, self.start))


class LintTag(unittest.TestCase):
    def lint(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(LINT), *args], capture_output=True, text=True)

    def test_passender_tag(self):
        r = self.lint("--tag", f"v{bv.aktuelle_version(ROOT)}")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_falscher_tag(self):
        r = self.lint("--tag", "v0.0.0")
        self.assertEqual(r.returncode, 1)
        self.assertIn("passt nicht zur Version", r.stdout)


if __name__ == "__main__":
    unittest.main()
