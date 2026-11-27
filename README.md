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
    references/feedback-vorlage.md       # Feedback-Text an die Delegation
    scripts/papiertext.py                # Papier-JSON → Text, Wortzahlen, Formalprüfung, Versionsvergleich
scripts/lint_skill.py                    # Skill-Lint (Versionen, Frontmatter, Verweise)
tests/                                   # Tests für papiertext.py mit Beispielpapieren
.github/workflows/lint.yml               # CI: plugin validate, Skill-Lint, Tests
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

## Lizenz

MIT – siehe [LICENSE](LICENSE).
