# Changelog

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/). Die Site hat keine
Versionsnummern; was vor diesem Eintrag geschah, steht in `git log`.

## [Unreleased]

### Fixed
- **Prüflisten vollständig:** `werkzeuge/methodenseiten.py` übernahm von einem Punkt unter
  `## Prüfen` nur die erste Zeile. Betroffen waren die Seiten 08 (zwei Punkte) und 09 (drei Punkte):
  Dort endeten Fragen mitten im Satz. Jetzt werden eingerückte Fortsetzungszeilen angehängt. Bei einer
  verschachtelten Liste unter einem Prüfpunkt bricht das Skript ab, statt still zu kürzen. Die Seiten
  08 und 09 sind neu erzeugt.

### Added
- `werkzeuge/test_methodenseiten.py`: 7 Tests für die Prüfliste (einzeilig, mehrzeilig, Ende an
  Leerzeile und Trenner, verschachtelte Liste). Gegen den alten Generator schlagen 5 davon fehl.
- **Herkunfts-Gate:** `werkzeuge/herkunft-check.sh` ruft das Gate aus `zfdw-ki-leitplanken` mit
  derselben Begriffsliste auf (`.herkunft-begriffe`, lokal verlinkt, per `.gitignore`
  ausgeschlossen). Ohne Begriffsliste bricht es ab (Exit 2), statt ohne Aussage grün zu melden.
- `.gitignore` (bisher keine).
