# Changelog

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/). Die Site hat keine
Versionsnummern; was vor diesem Eintrag geschah, steht in `git log`.

## [Unreleased]

### Added
- **Zahlen-Check** (`werkzeuge/zahlen-check.sh`): führt Guard-Suite und Rot-Beweis aus
  `zfdw-ki-leitplanken` aus und vergleicht Testfälle, Nicht-Treffer, Mutanten sowie die
  ausgelieferte Größe von HTML und CSS mit `index.html`. Läuft in CI als eigener Job.
  `werkzeuge/test_zahlen-check.sh` ist sein Rot-Beweis: 7 Verfälschungen, alle erkannt.
- `og:image` (1200 × 630, `/og-wirkarchitektur.png`, eigenes Motiv aus dem Favicon) auf Startseite
  und Methodenseiten; `favicon.ico` für Browser, die sie trotz Data-URI anfragen.
- Impressum und Datenschutz: `description` und `canonical`.
- **Dependabot für GitHub Actions** (`.github/dependabot.yml`): monatlich, gebündelt in einem PR. Die SHA-Pins der CI veralten sonst still.

### Changed
- CI prüft die Navigation mit Chromium bei 375 und 1440 px auf horizontalen Überlauf,
  außerdem Sprungziel, Mail-Anfrage, Kontaktlinks und Unterseiten-Fußzeilen.
- **T10:** Startnavigation auf Einstieg, Werkbank, Methode, Guard, Mit sitelook und Kontakt
  reduziert; Einordnung und Warum offen bleiben als Abschnitte erhalten. Früher Hinweis
  auf Einrichtung, Review und Schulung mit Sprung zu Mit sitelook; dort direkte Mail-Anfrage
  mit Betreff. Kontakt verweist auf öffentliche Issues und Pull Requests.
- Unterseiten einschließlich 404: Fußzeile um Mit sitelook und Kontakt ergänzt;
  Methodenseiten aus dem Generator erneuert. Impressum und Datenschutz erhalten `og:image`.
  Prüfpunkt zum Strato-Vertrag aus dem README entfernt.
- `styles.css` wird mit `?v=<Datum>` eingebunden und ein Jahr `immutable` gecacht (bisher 4 h).
  Bei jeder Änderung an `styles.css` das Datum in allen HTML-Dateien und im Generator mitziehen.
- Sitemap: Startseite `lastmod` 2026-10-22; Impressum und Datenschutz entfernt, weil beide `noindex`
  tragen.
- Quelltext-Kommentar der Startseite im Du, wie die Seite.

### Fixed
- **Zahlen der Startseite auf einen echten Lauf gezogen** (`zfdw-ki-leitplanken` `main` `e0c7f26`,
  22.10.2026): 48 statt 24 Testfälle, 16 statt 9 bewusste Nicht-Treffer, 11 statt 7 Mutanten
  (Aufzählung ergänzt), Beispielausgabe „48 bestanden“. Kolophon: 21,3 kB HTML und 7,4 kB CSS,
  gemessen wie ausgeliefert; `Permissions-Policy` wortgleich mit `/_headers`.
- **Navigation auf dem Handy:** bricht um statt über den Rand zu laufen (bei 375 px war sie 553 px
  breit). Schrift 0,9 rem statt 0,82 rem.
- Verweise auf Methode 07–10 zeigen auf die eigenen Methodenseiten statt auf `.md` bei GitHub.
- **Betonung kursiv statt Monospace:** `em` sah aus wie Code ohne Hintergrund.

- **Methode 01 zeigt ihre Prüfliste.** Der Generator suchte genau `## Prüfen`; Methode 01 nennt den
  Abschnitt `## Prüfen, ob es eingehalten wurde`, ihre Seite hatte deshalb keine Prüfliste. Jetzt
  zählt jede Überschrift, die mit dem Wort „Prüfen“ beginnt (nicht „Prüfenswert…“). Die
  Prüf-Überschrift steht wie bei den anderen Seiten nicht mehr zusätzlich in der Liste *Im
  Volltext*. Seite 01 neu erzeugt, die übrigen Seiten unverändert.
- **Prüflisten vollständig:** `werkzeuge/methodenseiten.py` übernahm von einem Punkt unter
  `## Prüfen` nur die erste Zeile. Betroffen waren die Seiten 08 (zwei Punkte) und 09 (drei Punkte):
  Dort endeten Fragen mitten im Satz. Jetzt werden eingerückte Fortsetzungszeilen angehängt. Bei einer
  verschachtelten Liste unter einem Prüfpunkt bricht das Skript ab, statt still zu kürzen. Die Seiten
  08 und 09 sind neu erzeugt.

### Added
- **CI** (`.github/workflows/tests.yml`): Generator-Tests und `methodenseiten.py --pruefen` gegen
  `zfdw-ki-leitplanken` `main` bei jedem PR und jedem Push auf `main`. Actions per Commit-SHA
  gepinnt, Token nur lesend. Das Herkunfts-Gate läuft bewusst nicht in CI (private Begriffsliste).
- `werkzeuge/test_methodenseiten.py`: 3 Tests zur Form der Prüf-Überschrift (Langform erkannt,
  „Prüfenswert…“ nicht, Langform nicht in der Abschnittsliste). Gegen den alten Generator schlagen 2
  davon fehl.
- `werkzeuge/test_methodenseiten.py`: 7 Tests für die Prüfliste (einzeilig, mehrzeilig, Ende an
  Leerzeile und Trenner, verschachtelte Liste). Gegen den alten Generator schlagen 5 davon fehl.
- **Herkunfts-Gate:** `werkzeuge/herkunft-check.sh` ruft das Gate aus `zfdw-ki-leitplanken` mit
  derselben Begriffsliste auf (`.herkunft-begriffe`, lokal verlinkt, per `.gitignore`
  ausgeschlossen). Ohne Begriffsliste bricht es ab (Exit 2), statt ohne Aussage grün zu melden.
- `.gitignore` (bisher keine).
