# papierkorrektur

Skill für Claude, der MUN-Positions- und Arbeitspapiere aus dem
MUNIFY DELEGATOR über dessen MCP-Server (https://delegator.munify.cloud/mcp) liest, nach
festen Kriterien bewertet und Feedback für Vorsitzende schreibt, inklusive einer Empfehlung
(ACCEPTED oder CHANGES_REQUESTED). Unsichere Stellen sind im Doc per Kommentar markiert. Nach
dem Prüfen legt Claude auf Wunsch einen Korrekturentwurf mit Grußformel im DELEGATOR an;
abschicken tut die vorsitzende Person. Aufruf zum Beispiel mit „Korrigier das nächste Positionspapier
im Menschenrechtsrat“ oder direkt über `/papierkorrektur:papierkorrektur`.

Installation in Claude Code:

```
/plugin marketplace add DeutscheModelUnitedNations/papierkorrektur-skill
/plugin install papierkorrektur@papierkorrektur
```

Voraussetzung: Anmeldung im DELEGATOR beim ersten Aufruf und freigeschaltete KI-Assistenten
für die Konferenz. Weitere Details im README des Repositorys.
