# papierkorrektur

Skill für Claude, der MUN-Papiere (Positions-, Arbeits- und Einführungspapiere) aus dem
MUNIFY DELEGATOR über dessen MCP-Server (https://delegator.munify.cloud/mcp) liest, nach
festen Kriterien bewertet und Feedback für Vorsitzende schreibt, inklusive einer Empfehlung
(ACCEPTED oder CHANGES_REQUESTED). Claude ändert nichts im DELEGATOR; die vorsitzende Person
trägt das Feedback selbst ein. Aufruf zum Beispiel mit „Korrigier das nächste Positionspapier
im Menschenrechtsrat“ oder direkt über `/papierkorrektur:papierkorrektur`.

Voraussetzung: Anmeldung im DELEGATOR beim ersten Aufruf und freigeschaltete KI-Assistenten
für die Konferenz. Weitere Details im README des Repositorys.
