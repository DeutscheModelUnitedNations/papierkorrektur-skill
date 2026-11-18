# Papierkorrektur

Claude-Plugin-Marketplace mit einem Skill, der MUN-Papiere (Positions-, Arbeits- und
Einführungspapiere) aus dem [MUNIFY DELEGATOR](https://delegator.munify.cloud) per MCP liest
und Korrektur-Feedback für Vorsitzende schreibt. Claude ändert dabei nichts im DELEGATOR:
Das Feedback trägt die vorsitzende Person selbst ein.

## Aufbau

```
.claude-plugin/marketplace.json          # Marketplace-Katalog
plugins/papierkorrektur/
  .claude-plugin/plugin.json             # Plugin-Manifest
  .mcp.json                              # MUNIFY-DELEGATOR-MCP (https://delegator.munify.cloud/mcp)
  skills/papierkorrektur/
    SKILL.md                             # Ablauf und Regeln
    references/mcp-abfragen.md           # getestete GraphQL-Abfragen
    references/bewertungskriterien.md    # Kriterien je Papiertyp
    references/feedback-vorlage.md       # Ausgabeformat
    scripts/tiptap_to_text.py            # TipTap-JSON → Markdown + Wortzahlen
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
python3 plugins/papierkorrektur/skills/papierkorrektur/scripts/tiptap_to_text.py antwort.json
```

Offen: Kriterien für Arbeits- und Einführungspapiere in `references/bewertungskriterien.md`.

## Lizenz

MIT – siehe [LICENSE](LICENSE).
