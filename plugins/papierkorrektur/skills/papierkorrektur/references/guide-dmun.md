# Gremientext aus dem DMUN-Guide holen

https://guide.dmun.de ist ein öffentlicher Ghost-Blog (kein Login). Pro Konferenz gibt es
genau eine, die jeweils aktuelle Ausgabe – **ohne Jahr in der URL**:

| Konferenz im DELEGATOR | Guide-Wurzel |
|---|---|
| MUNBW <Jahr> | https://guide.dmun.de/munbw/ |
| MUN-SH <Jahr> | https://guide.dmun.de/mun-sh/ |

Andere Konferenzen: Startseite https://guide.dmun.de/ ansehen; gibt es keine passende
Wurzel, nach Gremientext fragen (siehe unten).

## Volltext holen (Reihenfolge)

Die „Punkte zur Diskussion“ sollen **wörtlich** ins Doc. WebFetch fasst längere Seiten
zusammen, deshalb in dieser Reihenfolge:

1. **Ghost Content API** über das Skript (braucht Shell und Internet):
   ```bash
   python3 <skill-ordner>/scripts/guide.py suche "<Stichwort aus dem Titel>" --konferenz munbw
   python3 <skill-ordner>/scripts/guide.py text <slug-oder-url> --abschnitt "Punkte zur Diskussion"
   python3 <skill-ordner>/scripts/guide.py text <slug-oder-url>    # ganze Seite
   ```
   Der Schlüssel ist der öffentliche Suchschlüssel aus dem HTML der Seite (`data-key`), das
   Skript liest ihn selbst aus. Ohne Skript geht dasselbe per
   `https://guide.dmun.de/ghost/api/content/posts/slug/<slug>/?key=<data-key>`. Themenseiten
   sind Ghost-**Posts**, nicht Pages. RSS gibt es nicht.
2. **Browser** (Claude in Chrome oder eingebauter Browser): Themenseite öffnen, mit
   `get_page_text` lesen. Auch wörtlich.
3. **WebFetch** als letzter Weg. Dann stehen die Diskussionspunkte im Doc als
   „sinngemäß nach Gremientext“ (siehe dokument-aufbau.md). Für die Bewertung reicht das.

## Themenseite finden

Mit dem Skript: `suche` mit einem markanten Wort aus dem `agendaItem.title` (bei
abweichendem Wortlaut auch ein sinngleiches, z. B. „Klimaflucht“ für „Klimaflüchtlinge“).
Ohne Skript navigieren:

Slugs lassen sich **nicht** aus dem Titel ableiten und sind teils veraltet (der Slug
`sr-top-2-potentielle-bewaffnete-auseinandersetzungen-auf-dem-gebiet-der-taiwanstrasse`
zeigt z. B. „SR TOP 2: Schutz von Kulturschätzen/-stätten …“). Deshalb immer navigieren:

1. Die Guide-Wurzel der Konferenz öffnen.
2. In der Seitenleiste die Gremiengruppe finden (Kürzel wie GV, SR, MRR, WiSo, UV, IGH,
   WEK, ICAO; das DELEGATOR-Feld `committee.abbreviation` passt meist, Groß-/Kleinschreibung
   kann abweichen).
3. Die Themenlinks heißen „<Kürzel> TOP <n>: <Titel>“. Den Link nehmen, dessen **Titel zum
   `agendaItem.title` aus dem DELEGATOR passt**.
4. Die Seite lesen.

## Abgleich

Eindeutig ist es, wenn Gremium **und** Thementitel übereinstimmen (kleine Abweichungen in
Schreibweise oder Zusätzen sind ok). **Sinngleiche Titel gelten als Treffer** („Klimaflucht“
im Guide = „Klimaflüchtlinge“ im DELEGATOR). Die **Jahreszahl in der Beschriftung des
Guides ist kein Hinweis**: /munbw/ hieß z. B. „MUNBW 2025“, enthielt aber die Themen von
2026. Maßgeblich sind nur Gremium und Thementitel. In allen anderen Fällen fragst du nach – z. B. wenn
der Guide schon die nächste Ausgabe zeigt, das Thema fehlt oder zwei Themen ähnlich
klingen. Frag dann nach einem **Link, einer Datei oder dem kopierten Gremientext** und
nenne, was du gefunden hast.

## Aufbau einer Themenseite

Inhaltshinweis, dann die Abschnitte:
- Einleitung
- Hintergrund und Grundsätzliches
- Aktuelles
- Probleme und Lösungsansätze
- **Punkte zur Diskussion** ← daran misst du „mindestens drei Diskussionspunkte“
- Für die Recherche · Wichtige Dokumente · Quellenangaben · Lexikon

Merk dir für die Korrektur: die **Punkte zur Diskussion** (wörtlich, wenn über Weg 1 oder 2
geholt, sonst als „sinngemäß“ markiert), die
zentralen Fakten und Abkommen aus „Hintergrund“ und „Aktuelles“ sowie die Links unter
„Wichtige Dokumente“ (für Präambel-Verweise bei Arbeitspapieren).

## Weitere Guide-Seiten, die der Leitfaden nennt

- „Positionspapier schreiben“ – was Teilnehmenden zum Positionspapier gesagt wird.
- Abschnitt zum Arbeitspapier mit der **Liste der zugelassenen Operatoren**.

Beide liegen unter der Guide-Wurzel der Konferenz (Seitenleiste, meist in den
Schritt-Seiten des Gremiums). Lies sie, wenn du unsicher bist, was von Teilnehmenden
erwartet wird, oder ob ein Operator zugelassen ist.
