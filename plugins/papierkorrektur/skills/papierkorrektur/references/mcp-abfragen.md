# MCP-Abfragen für den MUNIFY DELEGATOR

Werkzeuge: `whoami`, `graphql_schema`, `graphql_query` (Präfix je nach Installation), dazu
das Werkzeug für **Korrekturentwürfe** (siehe unten) und `agenda_item_context` für Gremientext
und Punkte zur Diskussion eines Themas (gremientext.md). Alle Abfragen laufen über
`graphql_query` mit `conferenceId`. Getestet 2026-11.

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
| `Committeeagendaitem` | `id`, `title`, `teaserText`, `discussionPoints`, `committee`, `papers` |
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

**Die nächsten N Papiere:** dieselbe Abfrage mit `limit: N` in beiden Zweigen. Erst die
`submitted` nehmen; sind es weniger als N, mit `revised` in deren Reihenfolge auffüllen.

## Gremien und Themen einer Konferenz

Pro Gremium:

```graphql
{
  findPapersGroupedByCommittee(conferenceId: "<CONF>") { committee { id name abbreviation } }
  committeeAgendaItems(where: { committeeId: { eq: "<COMMITTEE>" } }) { id title }
}
```

Übersicht, wo Papiere warten (alle Themen der Konferenz, getestet 2026-11):

```graphql
{
  committeeAgendaItems(where: { committee: { conferenceId: { eq: "<CONF>" } } }) {
    id title committee { abbreviation }
    sub: papers(where: { status: SUBMITTED }) { id type }
    rev: papers(where: { status: REVISED })   { id type }
  }
}
```

Die Antwort kann groß werden (im Test über 400 Papiere). Für die Rückfrage an die Person nur
Zählungen pro Thema und Typ verwenden, keine ID-Listen.

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

Bei vielen Versionen den Inhalt nur für die neuesten laden, den Verlauf ohne `content`:

```graphql
{
  paper(id: "<PAPER>") {
    id type status firstSubmittedAt updatedAt
    delegation { assignedRole { name nationAlpha3Code kind } }
    agendaItem { id title teaserText committee { name abbreviation } }
    verlauf: versions(orderBy: { version: desc }) {
      version status createdAt reviews { statusBefore statusAfter createdAt }
    }
    neu: versions(orderBy: { version: desc }, limit: 2) { version content }
  }
}
```

Ist die zuletzt bewertete Version (die mit Review `statusAfter: CHANGES_REQUESTED`) nicht
unter den zwei neuesten, `neu` mit größerem `limit` erneut abfragen oder die Abfrage mit
allen Versionen nehmen – `papiertext.py --diff` meldet den Fall.

**Erst- oder Zweitkorrektur** entscheiden die Reviews, nicht die Versionsnummer: Hat keine
frühere Version ein Review, ist es eine Erstkorrektur (frühere Versionen waren Entwürfe oder
ohne Bewertung). Verglichen wird immer mit der zuletzt bewerteten Version.

Wenn eine Abfrage mit einem Feld- oder Filterfehler scheitert, schlag den Typ mit
`graphql_schema` nach und korrigiere sie, statt zu raten.

## Korrekturentwurf anlegen

Der DELEGATOR-MCP hat ein Werkzeug, das einen **Korrekturentwurf** (Review-Entwurf) zu einem
Papier schreibt. Abgeschickt wird der Entwurf erst von der vorsitzenden Person im DELEGATOR.
Nur in SKILL.md, Schritt 5 benutzen – nach Zustimmung.

- Werkzeug in der Werkzeugliste des DELEGATOR-Servers suchen (Name enthält in der Regel
  „draft“/„Entwurf“ und „review“). Den genauen Namen nicht raten.
- **Eingabeschema lesen**, bevor du es aufrufst: welche IDs es braucht (`paperId`, ggf.
  `conferenceId` oder Version), in welchem Format der Text erwartet wird (Markdown, HTML,
  TipTap-JSON) und ob es eine Statusempfehlung (`ACCEPTED` / `CHANGES_REQUESTED`) nimmt.
  Text im verlangten Format übergeben; Blockzitate bleiben Zitate (in HTML `<blockquote>`,
  in TipTap `blockquote`-Knoten), Grußformel nach feedback-vorlage.md.
- Gehört der Entwurf zu einer Version, die **bewertete Version** übergeben (die neueste).
- Fehler `FORBIDDEN`/fehlende Rechte: Die Person darf für dieses Gremium keine Reviews
  schreiben oder KI-Assistenten sind nicht freigeschaltet – sagen, nicht wiederholen.
- Nach dem Anlegen den Deeplink zur Korrekturseite nennen; dort liegt der Entwurf.
