# Aufbau des Korrektur-Dokuments

Ein Claude-Doc **pro Papier**. Vor dem ersten Docs-Aufruf: Docs-Skill laden, falls
vorhanden, sonst `guide( items = ["topic.index"] )` des Docs-Servers – dort stehen die
genauen Aufrufe (Geburt mit Pending-Blöcken, Abschnitt für Abschnitt füllen, Kommentare).
Diese Datei sagt nur, **was** hineinkommt.

## Titel

`<Staat/NA> · <Gremienkürzel> TOP: <Kurztitel> · <Positionspapier|Arbeitspapier> v<N>`
z. B. „Kenia · MRR · Zugang zur Justiz · Positionspapier v2“.
Staatsnamen auf Deutsch aus dem alpha-3-Code ableiten.

## Reihenfolge

Gleich nach dem Titel und der Byline (Datum · Person) als erste Zeile der Deeplink:
`**[Papier im DELEGATOR öffnen](https://delegator.munify.cloud/dashboard/<conferenceId>/paperhub/<paperId>)**`

Danach die Abschnitte:

### 1. Metadaten
Eine Tabelle (Feld | Wert):
- Konferenz
- Gremium (Name und Kürzel)
- Thema – verlinkt auf die Guide-Seite, sonst „Gremientext: von <Quelle>“
- Delegation (Staat/NA, alpha-3)
- Papiertyp
- Version: „<N> (von <N>)“ und Status der Version
- Erste Einreichung, letzte Änderung (Datum)
- Bisherige Reviews: je Datum + Übergang, z. B. „15.04.2026 SUBMITTED → CHANGES_REQUESTED“, oder „keine“
- Umfang: Wörter (Positionspapier) bzw. Absätze Präambel/operativ (Arbeitspapier)
- Papier-ID

### 2. Was hat sich geändert (nur ab Version 2)
Lead-Satz mit dem Kern („Abschnitt 5 neu geschrieben, Zusammenfassung gekürzt, sonst
unverändert.“), dann die Tabelle aus `papiertext.py --diff` (Abschnitt | vorher | jetzt |
Änderung). Keine Absatz-Diffs abdrucken. Darunter ein Satz zum früheren Feedback: woher
du es kennst (von der Person mitgegeben) oder dass es nicht vorlag.

### 3. Papiertext
Der Text der bewerteten Version **wörtlich**, so wie `papiertext.py` ihn ausgibt:
- Positionspapier: je Abschnitt `### <Titel>` und die Absätze; die Leitfrage weglassen.
  Fließtext ohne Gliederung bleibt ein Abschnitt.
- Arbeitspapier: `### Präambel` (P1, P2, …) und `### Operativer Teil` (1., 2., … mit
  eingerückten a), i.).

Nichts am Papiertext korrigieren oder umstellen – Zitate im Feedback müssen sich im
DELEGATOR wiederfinden lassen.

**Anmerkungen als Kommentare.** Erst wenn der Papiertext steht: für jede Anmerkung ein
Doc-Kommentar, verankert an 3–6 wörtlichen Wörtern der Stelle. Kommentar-Text beginnt mit
einem Etikett:
- `Kernpunkt 1:` … `Kernpunkt 3:` – die ~3 Punkte, die ins Feedback gehen
- `Hinweis:` – weitere Anmerkung, nicht im Feedback
- `Lob:` – konkrete Stärke, die im Feedback auftaucht
- `⚠ Warnung:` – schwerer Mangel (Faktenfehler, falsche Perspektive, Anzeichen für KI-Text,
  Pflichtteil fehlt)

Danach knapp: was auffällt, warum es zählt (Checklistenpunkt), ggf. Vorschlag. Kommentare
sind kurz (Karte ~40 Zeichen breit, ≤ 4 Zeilen).

**Warnmarker im Text.** Für jede `⚠ Warnung` zusätzlich am **Ende des betroffenen
Absatzes** ` **[⚠ <2–4 Wörter>]**` anhängen (z. B. „**[⚠ Faktenfehler: Mitgliedschaft]**“).
Nie mitten in einen Satz – sonst stimmen Zitate nicht mehr.

Fehlt etwas ganz (z. B. kein Diskussionspunkt behandelt), kommt der Kommentar an die
Abschnittsüberschrift oder an den ersten Satz des Papiers.

### 4. Bewertung
- **Checkliste** als Tabelle: Kriterium | ✓ / teilweise / ✗ | Beleg (kurz, ggf. Absatz
  oder Abschnitt). Kriterien aus `korrekturleitfaden.md` – beim Arbeitspapier die
  ergänzende Checkliste plus die passenden Punkte der Positionspapier-Liste. Ergebnisse der
  automatischen Formalprüfung übernehmen.
- **Diskussionspunkte:** Liste der „Punkte zur Diskussion“ aus dem Gremientext, je mit
  „behandelt in Abschnitt …“ oder „nicht behandelt“.
- **Die drei Kernpunkte** als nummerierte Liste (dieselben wie in den Kommentaren).

### 5. Klassifikation
Eine Zeile, fett, dann 1–2 Sätze Begründung:
- **Bitte überarbeiten** (im DELEGATOR: „Änderungen anfordern“ / CHANGES_REQUESTED)
- **Akzeptiert** (ACCEPTED) – darf kleinere Änderungswünsche enthalten; die dann als
  „Optional:“-Liste darunter.

### 6. Feedback-Text
Überschrift „Feedback-Text (zum Kopieren)“, ein Satz „Kann vor dem Einfügen angepasst
werden.“, dann der Text nach `feedback-vorlage.md`. Wörtliche Zitate als Markdown-Blockzitate
(`> …`), damit sie beim Kopieren als Zitat im DELEGATOR ankommen.

## Fallback ohne Claude Docs

Gibt es keinen Docs-Server, schreib dieselbe Struktur als Markdown-Datei in den
Arbeitsordner: `korrektur-<land>-<gremium>-<typ>-v<N>.md` (ASCII, klein, Bindestriche).
Kommentare werden zu Fußnoten direkt hinter der Stelle (`[^k1]`, Text mit demselben Etikett
am Ende des Abschnitts „Papiertext“); Warnmarker wie oben. Im Chat den Pfad nennen.
