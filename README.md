# Papierkorrektur

Claude-Plugin-Marketplace mit einem Skill, der MUN-Positions- und Arbeitspapiere aus dem
[MUNIFY DELEGATOR](https://delegator.munify.cloud) per MCP liest, Gremientext und Punkte zur Diskussion aus dem
Vorbereitungsleitfaden des DELEGATOR holt, nach dem DMUN-Korrekturleitfaden bewertet und
pro Papier ein Claude-Doc mit kommentiertem Papiertext, Klassifikation und Feedback-Text anlegt.
Unsichere Einschätzungen markiert Claude dort per Kommentar. Nach dem Drüberschauen legt Claude
auf Wunsch den (ggf. angepassten) Feedback-Text mit Grußformel als Korrekturentwurf im DELEGATOR
an; abschicken und Status setzen tut die vorsitzende Person selbst.

## Aufbau

```
.claude-plugin/marketplace.json          # Marketplace-Katalog
plugins/papierkorrektur/
  .claude-plugin/plugin.json             # Plugin-Manifest
  .mcp.json                              # MUNIFY-DELEGATOR-MCP (https://delegator.munify.cloud/mcp)
  skills/papierkorrektur/
    SKILL.md                             # Ablauf und Regeln
    references/korrekturleitfaden.md     # Maßstab und Checklisten (Korrekturleitfaden MUN-SH 2027)
    references/gremientext.md            # Gremientext und Punkte zur Diskussion aus dem DELEGATOR
    references/mcp-abfragen.md           # getestete GraphQL-Abfragen, Deeplinks
    references/dokument-aufbau.md        # Aufbau des Korrektur-Docs
    references/feedback-vorlage.md       # Feedback-Text an die Delegation: feste Regeln, Zitate
    references/feedback-formen.md        # Formen, Einstiege, Schlüsse (vom Skript gelesen), abgenutzte Wendungen
    scripts/papiertext.py                # Papier-JSON → Text, Wortzahlen, Formalprüfung, Versionsvergleich; --form
scripts/lint_skill.py                    # Skill-Lint (Versionen, Frontmatter, Verweise; --tag)
scripts/bump_version.py                  # Versionsnummer an allen Stellen setzen
tests/                                   # Tests für papiertext.py, bump_version.py und den Tag-Check
.github/workflows/lint.yml               # CI: plugin validate, Skill-Lint, Tests; bei Tags: Tag = Version
.github/workflows/release.yml            # Release: Bump-PR öffnen, nach dem Merge Tag + Release
```

## Installation

In Claude Code (das Repo ist privat, also braucht es Zugriff auf die GitHub-Organisation
DeutscheModelUnitedNations):

```
/plugin marketplace add DeutscheModelUnitedNations/papierkorrektur-skill
/plugin install papierkorrektur@papierkorrektur
```

Lokal zum Testen:

```
/plugin marketplace add /pfad/zu/papierkorrektur-skill
/plugin install papierkorrektur@papierkorrektur
```

Beim ersten Aufruf fragt der MCP-Server nach der Anmeldung im DELEGATOR (OAuth über `/mcp`).
Die Projektleitung der Konferenz muss KI-Assistenten freigeschaltet haben.

Wer den DELEGATOR schon als claude.ai-Connector verbunden hat, bekommt die Werkzeuge
doppelt. Das stört nicht; wer es vermeiden will, löscht `plugins/papierkorrektur/.mcp.json`.

## Entwicklung

```bash
claude plugin validate .
```

```bash
python3 plugins/papierkorrektur/skills/papierkorrektur/scripts/papiertext.py antwort.json --diff
```

```bash
python3 plugins/papierkorrektur/skills/papierkorrektur/scripts/papiertext.py --form --klassifikation ueberarbeiten --seed 1
```

Vor dem Push (läuft auch in der CI, `.github/workflows/lint.yml`):

```bash
python3 scripts/lint_skill.py
```

```bash
python3 -m unittest discover -s tests -v
```

`lint_skill.py` prüft, ob die Versionsnummern in `marketplace.json` und `plugin.json`
übereinstimmen, ob `name` und `description` im Frontmatter von `SKILL.md` gültig sind
(`description` höchstens 1024 Zeichen, ab 950 gibt es eine Warnung) und ob alle relativen
Verweise in den Markdown-Dateien des Skills auf vorhandene Dateien zeigen. Die Tests in
`tests/` prüfen `papiertext.py` gegen von Hand gebaute Beispielpapiere in `tests/fixtures/`.

Offen: Abschnitte „Typische Fehler und Textbausteine“ des Korrekturleitfadens (im Original noch in Arbeit).

## Release

Die Version steht in `.claude-plugin/marketplace.json` (`metadata.version` und beim Plugin) und in
`plugins/papierkorrektur/.claude-plugin/plugin.json`. Claude Code erkennt Updates an dieser Nummer,
also gehört zu jedem Release ein Bump. Nicht von Hand ändern, sondern:

1. Actions → **Release** → „Run workflow“, `patch`/`minor`/`major` wählen oder eine feste Version
   eintragen. Der Workflow zählt hoch, lässt Lint und Tests laufen und öffnet den PR „Version X.Y.Z“
   von `release/vX.Y.Z` gegen `main`.
2. PR mergen.
3. Der Push auf `main` legt Tag und GitHub-Release `vX.Y.Z` auf dem Merge-Commit an, mit
   automatisch erzeugten Release Notes. Gibt es die Version schon, passiert nichts.

Wird doch einmal ein Tag von Hand gepusht, prüft `lint.yml`, ob er zur Version in den Dateien passt.

Voraussetzungen im Repo: Unter Settings → Actions → General muss „Allow GitHub Actions to create
and approve pull requests“ an sein. Mit dem Standard-Token laufen am Bump-PR keine Checks
(GitHub startet für Bot-Pushes keine Workflows). Abhilfe: das Secret `RELEASE_TOKEN` anlegen
(fine-grained PAT oder App-Token mit `contents` und `pull-requests: write`) oder den PR einmal
schließen und wieder öffnen.

Lokal geht der Bump auch ohne CI:

```bash
python3 scripts/bump_version.py minor
```

## Lizenz

MIT – siehe [LICENSE](LICENSE).
