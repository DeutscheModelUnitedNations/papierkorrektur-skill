# MCP-Abfragen für den MUNIFY DELEGATOR

Alle Abfragen laufen über `graphql_query` mit `conferenceId`. Die Beispiele sind gegen
den Server getestet (Stand 2026-11). Gotchas:

- ID-Filter nutzen `{ eq: "…" }` (nicht `equals`).
- Der Status-Filter auf `Paper` nimmt **einen** Enum-Wert direkt: `where: { status: SUBMITTED }`.
  `in` geht nicht – für `SUBMITTED` und `REVISED` zwei Abfragen oder zwei Aliasse.
- `Paper` lässt sich nicht nach Konferenz filtern – geh über Gremien bzw. Tagesordnungspunkte.
- Den Staat einer Delegation liefert `delegation.assignedRole.nationAlpha3Code` (klein,
  z. B. `eth`). `name` ist bei Staaten meist `null`; bei NGOs o. Ä. (`kind` ≠ `NATION`) steht er dort.

## Datenmodell (Auszug)

| Typ | Wichtige Felder |
|---|---|
| `Paper` | `id`, `type` (`POSITION_PAPER`, `WORKING_PAPER`, `INTRODUCTION_PAPER`), `status`, `delegation`, `agendaItem`, `firstSubmittedAt`, `versions` |
| `Paperversion` | `version`, `status`, `content` (TipTap-JSON als String), `reviews` |
| `Paperreview` | `statusBefore`, `statusAfter`, `createdAt`, `comments` (**redacted**) |
| `Committeeagendaitem` | `id`, `title`, `teaserText`, `committee`, `reviewHelpStatus`, `papers` |
| `Committee` | `id`, `name`, `abbreviation` |

Status: `DRAFT` → `SUBMITTED` → `CHANGES_REQUESTED` → `REVISED` → … → `ACCEPTED`.

## Gremien der Konferenz

```graphql
{
  findPapersGroupedByCommittee(conferenceId: "<CONF>") {
    committee { id name abbreviation }
  }
}
```

## Offene Papiere eines Gremiums

```graphql
{
  committeeAgendaItems(where: { committeeId: { eq: "<COMMITTEE>" } }) {
    id title teaserText
    submitted: papers(where: { status: SUBMITTED }) {
      id type firstSubmittedAt
      delegation { assignedRole { name nationAlpha3Code } }
    }
    revised: papers(where: { status: REVISED }) {
      id type firstSubmittedAt
      delegation { assignedRole { name nationAlpha3Code } }
    }
  }
}
```

## Nächstes Papier zur Korrektur

```graphql
{
  findNextPaperToReview(agendaItemId: "<AGENDA_ITEM>") {
    id type status
    delegation { assignedRole { name nationAlpha3Code } }
    agendaItem { title teaserText committee { abbreviation } }
    versions(orderBy: { version: desc }, limit: 1) { version status content }
  }
}
```

## Ein Papier mit Versionsverlauf

```graphql
{
  paper(id: "<PAPER>") {
    id type status
    delegation { assignedRole { name nationAlpha3Code } }
    agendaItem { title teaserText committee { abbreviation } }
    versions(orderBy: { version: desc }) {
      version status createdAt content
      reviews { statusBefore statusAfter createdAt }
    }
  }
}
```

Für das Skript die Antwort in eine Datei schreiben (z. B. im Scratchpad) und den Pfad
übergeben; das Skript nimmt die erste Version mit TipTap-Inhalt, also die neueste, wenn
absteigend sortiert.

Wenn eine Abfrage mit einem Feld- oder Filterfehler scheitert, schlag den Typ mit
`graphql_schema` nach und korrigiere die Abfrage, statt zu raten.
