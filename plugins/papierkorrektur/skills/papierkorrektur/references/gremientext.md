# Gremientext und Punkte zur Diskussion aus dem DELEGATOR

Gremientext und Punkte zur Diskussion stehen im **Vorbereitungsleitfaden des DELEGATOR**,
auf der Seite des Themas. Du liest sie mit einem Aufruf des DELEGATOR-MCP:

```
agenda_item_context(conferenceId: "<CONF>", agendaItemId: "<agendaItem.id des Papiers>")
```

Die `agendaItem.id` steht schon in den Metadaten des Papiers (mcp-abfragen.md, „Ein Papier
mit allen Versionen“). Das Werkzeug braucht die Rolle zum Begutachten von Papieren oder
Leitfaden-Rechte in der Konferenz, wie die Korrektur selbst.

## Was zurückkommt

| Feld | Inhalt |
|---|---|
| `agendaItem` | Titel, Teaser, Gremium (Name, Kürzel) |
| `discussionPoints` | die **Punkte zur Diskussion**, wörtlich, in ihrer Reihenfolge |
| `discussionPointsSource` | woher sie kommen: `agendaItem` (beim Thema gepflegt), `committeeText` (aus dem Abschnitt „Punkte zur Diskussion“ im Gremientext gelesen) oder `none` |
| `committeeText` | die **veröffentlichte** Seite des Themas: `title`, `markdown` (der ganze Text), `versionNumber`, `publishedAt`, `pageId`, `pdfUrl` (kurzlebiger Link aufs PDF); `null`, solange nichts veröffentlicht ist |
| `note` | Hinweise, wenn etwas fehlt |

Im `markdown` steht an der Stelle der Punkte zur Diskussion oft nur der Platzhalter
`{{Diskussionspunkte}}` – die Punkte selbst nimmst du aus `discussionPoints`. Hinweisboxen,
Aufklappbereiche und Buttons fehlen im Markdown (`omittedBlocks` nennt sie); für die
Korrektur reicht der Text.

Link zur Seite des Themas (für die Metadaten im Doc):
`https://delegator.munify.cloud/dashboard/<conferenceId>/guide/<committeeText.pageId>`

## Was du dir merkst

- die **Punkte zur Diskussion** wörtlich aus `discussionPoints` – daran misst du
  „mindestens drei Diskussionspunkte“;
- die zentralen Fakten und Abkommen aus Hintergrund und Aktuellem des Gremientexts;
- die wichtigen Dokumente und Quellen (für Präambel-Verweise bei Arbeitspapieren).

## Wenn etwas fehlt

- **`committeeText` ist `null`** (Seite nicht veröffentlicht): sag das und bitte um den
  Gremientext als Datei oder kopierten Text. Nicht erfinden, nicht im Netz suchen.
- **`discussionPointsSource` ist `none`**: Das Thema hat keine Punkte zur Diskussion und der
  Gremientext nennt keine. Steht im Text etwas Gleichwertiges unter anderer Überschrift
  (etwa „Leitfragen“), nimm das und setz einen `? Unsicher:`-Kommentar an die
  Diskussionspunkte im Doc. Sonst frag nach, bevor du das Kriterium bewertest.
- **Das Werkzeug gibt es nicht** (älterer DELEGATOR) **oder es lehnt ab** (fehlende
  Rolle): sag das und bitte um den Gremientext als Datei oder kopierten Text.

Text, den die Person selbst liefert, gilt wie ein Gremientext aus dem DELEGATOR; im Doc
steht dann „Gremientext: von der vorsitzenden Person“.
