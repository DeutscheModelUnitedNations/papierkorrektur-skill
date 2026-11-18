# Papierkorrektur

Claude-Plugin-Marketplace mit einem Skill, der MUN-Positions- und Arbeitspapiere aus dem
[MUNIFY DELEGATOR](https://delegator.munify.cloud) per MCP liest, den Gremientext aus
[guide.dmun.de](https://guide.dmun.de) holt, nach dem DMUN-Korrekturleitfaden bewertet und
pro Papier ein Claude-Doc mit kommentiertem Papiertext, Klassifikation und Feedback-Text anlegt. Claude ändert dabei nichts im DELEGATOR:
Das Feedback trägt die vorsitzende Person selbst ein.

## Aufbau

```
.claude-plugin/marketplace.json          # Marketplace-Katalog
plugins/papierkorrektur/
  .claude-plugin/plugin.json             # Plugin-Manifest
  .mcp.json                              # MUNIFY-DELEGATOR-MCP (https://delegator.munify.cloud/mcp)
  skills/papierkorrektur/
    SKILL.md                             # Ablauf und Regeln
    references/korrekturleitfaden.md     # Maßstab und Checklisten (Korrekturleitfaden MUN-SH 2027)
    references/guide-dmun.md             # Gremientext auf guide.dmun.de finden
    references/mcp-abfragen.md           # getestete GraphQL-Abfragen, Deeplinks
    references/dokument-aufbau.md        # Aufbau des Korrektur-Docs
    references/feedback-vorlage.md       # Feedback-Text an die Delegation
    scripts/papiertext.py                # Papier-JSON → Text, Wortzahlen, Formalprüfung, Versionsvergleich
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

Offen: Abschnitte „Typische Fehler und Textbausteine“ des Korrekturleitfadens (im Original noch in Arbeit).

## Lizenz

MIT – siehe [LICENSE](LICENSE).
