# MCP-Abfragen für den MUNIFY DELEGATOR

Werkzeuge: `whoami`, `graphql_schema`, `graphql_query` (Präfix je nach Installation).
Alle Abfragen laufen über `graphql_query` mit `conferenceId`. Getestet 2026-11.

## Gotchas

- ID-Filter: `{ eq: "…" }` (nicht `equals`).
- Enum-Filter direkt: `where: { status: SUBMITTED, type: POSITION_PAPER }`; `in` geht nicht.
- Sortieren: `orderBy: { updatedAt: asc }`, Versionen `orderBy: { version: desc }`.
- `Paper` lässt sich nicht nach Konferenz filtern – über Gremium → Tagesordnungspunkt gehen.
- Staat einer Delegation: `delegation.assignedRole.nationAlpha3Code` (klein, z. B. `eth`).
  `name` ist bei Staaten meist `null`; bei NA (`kind` ≠ `NATION`) steht dort der Name.
- `Paperreview.comments` und alle Personendaten sind **redacted**. Frühere Feedbacks sind
  also nicht lesbar – nur Status-Übergänge und Zeitpunkte.
- `findNextPaperToReview` ist nur für das Papier-Team erlaubt (sonst FORBIDDEN).

## Deeplinks

- Korrekturseite: `https://delegator.munify.cloud/dashboard/<conferenceId>/paperhub/<paperId>`
- Leseansicht: `https://delegator.munify.cloud/dashboard/<conferenceId>/paperhub/view/<paperId>`

Ins Dok kommt immer der Link zur **Korrekturseite**.

## Datenmodell (Auszug)

| Typ | Wichtige Felder |
|---|---|
| `Paper` | `id`, `type` (`POSITION_PAPER`, `WORKING_PAPER`, `INTRODUCTION_PAPER`), `status`, `firstSubmittedAt`, `updatedAt`, `delegation`, `agendaItem`, `versions` |
| `Paperversion` | `version`, `status`, `createdAt`, `content` (JSON-String), `reviews` |
| `Paperreview` | `statusBefore`, `statusAfter`, `createdAt`, `comments` (redacted) |
| `Committeeagendaitem` | `id`, `title`, `teaserText`, `committee`, `papers` |
| `Committee` | `id`, `name`, `abbreviation` |

Status: `DRAFT` → `SUBMITTED` → `CHANGES_REQUESTED` ⇄ `REVISED` → `ACCEPTED`.
`content`: Positionspapier = TipTap-JSON, Arbeitspapier = Resolutions-JSON
(`preamble[]`, `operative[]` mit verschachtelten `subclauses`).

## Papiere auflösen

### a) Link
Aus `…/dashboard/<conferenceId>/paperhub/[view/]<paperId>` beide IDs nehmen → Abfrage „Ein Papier“.

### b) Nur Papier-ID
`whoami` → die Konferenzen der Reihe nach mit „Ein Papier“ probieren, bis eine antwortet.

### c) Land + Gremium + Konferenz
1. Konferenz über den Titel aus `whoami` (z. B. „MUN-SH 2027“).
2. Gremium über `findPapersGroupedByCommittee` (Name oder Kürzel).
3. Land in den ISO-alpha-3-Code übersetzen (Deutschland → `deu`, Äthiopien → `eth`).
4. Papiere des Gremiums laden und lokal nach `nationAlpha3Code` filtern:

```graphql
{
  committeeAgendaItems(where: { committeeId: { eq: "<COMMITTEE>" } }) {
    id title
    papers(where: { type: POSITION_PAPER }) {
      id type status updatedAt
      delegation { assignedRole { name nationAlpha3Code } }
    }
  }
}
```

Mehrere Treffer (mehrere Themen oder Typen) → nachfragen oder alle nehmen, wenn die Person
„alle“ gesagt hat.

### d) Nichts Bestimmtes → nächstes Papier eines Themas
Ohne Typwunsch: die DELEGATOR-Logik direkt.

```graphql
{
  findNextPaperToReview(agendaItemId: "<AGENDA_ITEM>") { id type status }
}
```

Mit Typwunsch dieselbe Logik nachbauen (neue Einreichungen vor Überarbeitungen, jeweils
das am längsten unberührte zuerst):

```graphql
{
  committeeAgendaItems(where: { id: { eq: "<AGENDA_ITEM>" } }) {
    submitted: papers(where: { type: POSITION_PAPER, status: SUBMITTED }, orderBy: { updatedAt: asc }, limit: 1) { id }
    revised:   papers(where: { type: POSITION_PAPER, status: REVISED },   orderBy: { updatedAt: asc }, limit: 1) { id }
  }
}
```

Erst `submitted`, sonst `revised`. Beides leer → „Für dieses Thema wartet kein Papier.“

## Gremien und Themen einer Konferenz

```graphql
{
  findPapersGroupedByCommittee(conferenceId: "<CONF>") { committee { id name abbreviation } }
  committeeAgendaItems(where: { committeeId: { eq: "<COMMITTEE>" } }) { id title }
}
```

## Ein Papier mit allen Versionen

```graphql
{
  paper(id: "<PAPER>") {
    id type status firstSubmittedAt updatedAt
    delegation { assignedRole { name nationAlpha3Code kind } }
    agendaItem { id title teaserText committee { name abbreviation } }
    versions(orderBy: { version: desc }) {
      version status createdAt content
      reviews { statusBefore statusAfter createdAt }
    }
  }
}
```

Bei sehr vielen Versionen reicht `versions(orderBy: { version: desc }, limit: 2)` für
neueste Version und Vorversion; den Verlauf (Anzahl Versionen, Review-Zeitpunkte) dann
separat ohne `content` abfragen.

Wenn eine Abfrage mit einem Feld- oder Filterfehler scheitert, schlag den Typ mit
`graphql_schema` nach und korrigiere sie, statt zu raten.
