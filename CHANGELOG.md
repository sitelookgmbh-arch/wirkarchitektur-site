# Changelog

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/). Die Site hat keine
Versionsnummern; was vor diesem Eintrag geschah, steht in `git log`.

## [Unreleased]

### Added
- **Dependabot für GitHub Actions** (`.github/dependabot.yml`): monatlich, gebündelt in einem PR. Die SHA-Pins der CI veralten sonst still.

### Fixed
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
