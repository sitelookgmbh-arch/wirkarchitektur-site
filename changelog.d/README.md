# Änderungsnotizen

Jeder neue PR ergänzt ausschließlich eine eigene Datei `changelog.d/<slug>.md`
mit einem eindeutigen Namen aus Kleinbuchstaben, Ziffern und Bindestrichen.
`CHANGELOG.md` und seine bestehenden Unreleased-Einträge bleiben dabei unverändert.
Fragmente sind öffentlich und müssen vor Veröffentlichung die Herkunftsprüfung bestehen.

Die erste Zeile ist genau `Added`, `Changed`, `Fixed` oder `Security`, danach folgen
Listenpunkte im bisherigen Keep-a-Changelog-Stil. Fortsetzungen werden mit mindestens
zwei Leerzeichen eingerückt. Beispiel:

```markdown
Fixed
- Beschreibe die sichtbare Korrektur.
  Ergänze bei Bedarf eine Fortsetzung.
```

## Bewusst sammeln

In einem sauberen Arbeitsbranch (nicht `main` oder `master`):

```bash
bash werkzeuge/changelog-sammeln.sh 1.0.0 --dry-run
bash werkzeuge/changelog-sammeln.sh 1.0.0
```

Die Version ist eine explizite Kennung für die Sammlung im Format X.Y.Z, kein
automatischer Release. Der Probelauf zeigt den neuen Abschnitt ohne Schreibzugriffe.
Der Sammler fügt ihn nach Unreleased und vor älteren Versionen ein; bestehende
Einträge bleiben erhalten. Reihenfolge: Added, Changed, Fixed, Security; innerhalb
eines Abschnitts nach Dateiname. Fragmente wandern nach `archive/<version>/`.
README und archivierte Fragmente werden nicht gesammelt.

Fehlende/ungültige Version, schmutziger Baum (auch unversionierte Dateien), ungültige
Fragmente, vorhandene Version/Archivziel oder fehlende Fragmente führen zum Abbruch.
Der Sammler führt keinen Commit, Push oder Tag aus. Änderungen vor einem eigenen
PR prüfen; die Veröffentlichung bleibt ein separater Schritt.
