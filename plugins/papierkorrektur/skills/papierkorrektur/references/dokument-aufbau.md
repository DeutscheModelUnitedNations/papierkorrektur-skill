# Aufbau des Korrektur-Dokuments

Ein Claude-Doc **pro Papier**. Vor dem ersten Docs-Aufruf: Docs-Skill laden, falls
vorhanden, sonst `guide( items = ["topic.index"] )` des Docs-Servers – dort stehen die
genauen Aufrufe (Geburt mit Pending-Blöcken, Abschnitt für Abschnitt füllen, Kommentare).
Diese Datei sagt nur, **was** hineinkommt.

## Titel

`<Staat/NA> · <Gremienkürzel> TOP: <Kurztitel> · <Positionspapier|Arbeitspapier> v<N>`
z. B. „Kenia · MRR · Zugang zur Justiz · Positionspapier v2“.
Staatsnamen auf Deutsch aus dem alpha-3-Code ableiten. `v<N>` ist immer die
DELEGATOR-Versionsnummer, auch wenn die Versionen davor nur Entwürfe waren.

## Reihenfolge

Gleich nach dem Titel und der Byline (Datum · Person) als erste Zeile der Deeplink:
`**[Papier im DELEGATOR öffnen](https://delegator.munify.cloud/dashboard/<conferenceId>/paperhub/<paperId>)**`

Danach die Abschnitte:

### 1. Metadaten
Eine Tabelle (Feld | Wert):
- Konferenz
- Gremium (Name und Kürzel)
- Thema – verlinkt auf seine Seite im Leitfaden des DELEGATOR (gremientext.md), sonst „Gremientext: von der vorsitzenden Person“
- Delegation (Staat/NA, alpha-3)
- Papiertyp
- Version: „<N> (von <N>)“ und Status der Version
- Korrektur: „Erstkorrektur“ (ggf. „Versionen 1–<N-1> waren Entwürfe“) oder
  „Zweitkorrektur, zuletzt bewertet: Version <M>“; textgleiche Folgeversionen benennen
  („Version 6 ist textgleich mit Version 5“). `papiertext.py` gibt diese Zeilen aus.
- Erste Einreichung, letzte Änderung (Datum)
- Bisherige Reviews: je Datum + Übergang, z. B. „15.04.2026 SUBMITTED → CHANGES_REQUESTED“, oder „keine“
- Umfang: Wörter (Positionspapier) bzw. Absätze Präambel/operativ (Arbeitspapier)
- Papier-ID

### 2. Was hat sich geändert (nur bei Zweitkorrektur)
Nur wenn eine frühere Version **ein Review** hat. Entwürfe (`DRAFT`) und Versionen ohne
Review zählen nicht – sonst fällt der Abschnitt weg, auch bei Version 6. Verglichen wird
mit der **zuletzt bewerteten Version** (Review mit `statusAfter: CHANGES_REQUESTED`), nicht
mit der direkten Vorversion; `papiertext.py --diff` macht das von selbst. Ist die neue
Version textgleich mit der bewerteten, steht hier nur dieser eine Satz.

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

**Anmerkungen als Kommentare.** Gleich nachdem der Papiertext steht, **vor** Bewertung und
Feedback-Text: für jede Anmerkung ein Doc-Kommentar, verankert an 3–6 wörtlichen Wörtern
der Stelle, **immer mit `"nth": 1`** im Anker. Die Zitate tauchen später im Feedback-Text
ein zweites Mal auf; das erste Vorkommen ist die Stelle im Papiertext. Kommentar-Text beginnt mit
einem Etikett:
- `Kernpunkt 1:` … `Kernpunkt 3:` – die ~3 Punkte, die ins Feedback gehen
- `Hinweis:` – weitere Anmerkung, nicht im Feedback
- `Lob:` – konkrete Stärke, die im Feedback auftaucht
- `⚠ Warnung:` – schwerer Mangel (Faktenfehler, falsche Perspektive, Anzeichen für KI-Text,
  Pflichtteil fehlt)
- `? Unsicher:` – du bist dir bei der Einschätzung nicht sicher (siehe „Unsicherheiten“)

Ist eine Warnung zugleich Kernpunkt, beides kombinieren: `⚠ Warnung (Kernpunkt 1): …`.

Danach knapp: was auffällt, warum es zählt (Checklistenpunkt), ggf. Vorschlag. Kommentare
sind kurz (Karte ~40 Zeichen breit, ≤ 4 Zeilen).

**Warnmarker im Text.** Für jede `⚠ Warnung` zusätzlich am **Ende des betroffenen
Absatzes** ` **[⚠ <2–4 Wörter>]**` anhängen (z. B. „**[⚠ Faktenfehler: Mitgliedschaft]**“).
Nie mitten in einen Satz – sonst stimmen Zitate nicht mehr.

Unsicherheit lässt sich mit den anderen Etiketten kombinieren: `? Unsicher (Kernpunkt 2): …`.

Fehlt etwas ganz (z. B. kein Diskussionspunkt behandelt), kommt der Kommentar an die
Abschnittsüberschrift oder an den ersten Satz des Papiers.

### 4. Bewertung
- **Checkliste** als Tabelle: Kriterium | ✓ / teilweise / ✗ | Beleg (kurz, ggf. Absatz
  oder Abschnitt). Kriterien aus `korrekturleitfaden.md` – beim Arbeitspapier die
  ergänzende Checkliste plus die passenden Punkte der Positionspapier-Liste. Ergebnisse der
  automatischen Formalprüfung übernehmen.
- **Diskussionspunkte:** Liste der „Punkte zur Diskussion“ wörtlich aus `discussionPoints`
  (gremientext.md), je mit „behandelt in Abschnitt …“ oder „nicht behandelt“.
- **Die drei Kernpunkte** als nummerierte Liste (dieselben wie in den Kommentaren).
- Als letzte Zeile, klein: „Feedback-Form: <Form>“ (SKILL.md, Schritt 3) – nur für die
  vorsitzende Person, nicht im Feedback-Text.

### 5. Klassifikation
Eine Zeile, fett, dann 1–2 Sätze Begründung:
- **Bitte überarbeiten** (im DELEGATOR: „Änderungen anfordern“ / CHANGES_REQUESTED)
- **Akzeptiert** (ACCEPTED) – darf kleinere Änderungswünsche enthalten; die dann als
  „Optional:“-Liste darunter.

### 6. Feedback-Text
Überschrift „Feedback-Text (zum Kopieren)“, ein Satz „Kann vor dem Einfügen angepasst
werden.“, dann der Text nach `feedback-vorlage.md`. Wörtliche Zitate als Markdown-Blockzitate
(`> …`), damit sie beim Kopieren als Zitat im DELEGATOR ankommen.

## Unsicherheiten

Jede Stelle, bei der du nicht sicher bist, bekommt einen Kommentar `? Unsicher: …` – so
sieht die vorsitzende Person beim Drüberschauen sofort, wo sie selbst urteilen muss.
Typische Fälle:
- Fakt im Papier, den du nicht sicher prüfen kannst (Zahl, Mitgliedschaft, Abstimmungsverhalten),
- Diskussionspunkt nur teilweise oder nur indirekt behandelt,
- Stelle, die man so oder so lesen kann (Perspektive, Ironie, Tippfehler oder Absicht),
- Grenzfall bei der Klassifikation („knapp überarbeiten“ / „knapp akzeptiert“),
- Punkte zur Diskussion nicht beim Thema gepflegt, sondern aus einer anderen Überschrift des Gremientexts genommen, oder Gremientext nicht ganz passend zum Thema.

Inhalt: **was** unsicher ist, **warum**, und **was** die Person prüfen oder entscheiden
sollte – kurz, ≤ 4 Zeilen.

Wo verankern:
- am Papiertext (wie die anderen Kommentare, `"nth": 1`), wenn es um eine Stelle im Papier geht;
- an der Zeile in der **Checkliste**, am Eintrag bei den **Diskussionspunkten** oder an der
  **Klassifikation**, wenn die Bewertung selbst unsicher ist;
- an einem Satz im **Feedback-Text**, wenn eine Formulierung dort auf einer unsicheren
  Annahme beruht. Anker dann aus deinem eigenen Text (nicht aus einem Blockzitat), damit
  er eindeutig ist; sonst das richtige `nth` wählen.

Keine Unsicherheit erfinden, um vorsichtig zu wirken – nur echte Zweifel. Im Feedback-Text
selbst taucht das Etikett nie auf.

## Fallback ohne Claude Docs

Gibt es keinen Docs-Server, schreib dieselbe Struktur als Markdown-Datei in den
Arbeitsordner: `korrektur-<land>-<gremium>-<typ>-v<N>.md` (ASCII, klein, Bindestriche).
Kommentare werden zu Fußnoten direkt hinter der Stelle (`[^k1]`, Text mit demselben Etikett
am Ende des Abschnitts „Papiertext“; `? Unsicher:` an Bewertung oder Feedback-Text am Ende
des jeweiligen Abschnitts); Warnmarker wie oben. In Schritt 5 die Datei statt des Docs neu
lesen. Im Chat den Pfad nennen.
