# wirkarchitektur.de

Statische Seite. Handgeschriebenes HTML, ein Stylesheet, **kein Build**, keine
Dependencies. Deploy = Dateien hochladen.

```
index.html        Startseite
impressum.html    § 5 DDG
datenschutz.html  DSGVO
404.html          ehrlicher 404 statt Weiterleitung
styles.css        das einzige Stylesheet
_headers          CSP + Security-Header (Cloudflare Pages)
_redirects        .com und Langform -> wirkarchitektur.de
robots.txt · sitemap.xml
methode/          Methodenseiten — ERZEUGT, nicht von Hand ändern (s. u.)
werkzeuge/        methodenseiten.py: erzeugt methode/ + Sitemap-Block, prüft Drift
                  zahlen-check.sh: Zahlen der Startseite gegen echten Lauf (s. u.)
                  test_methodenseiten.py: Tests des Generators (Prüfliste)
                  herkunft-check.sh: Herkunfts-Gate vor jedem PR (s. u.)
.github/          CI: Generator-Tests + Drift gegen zfdw-ki-leitplanken main (s. u.)
```

## Die Zusage der Seite

`default-src 'none'` in `/_headers`. Kein Skript, keine externe Schriftart, kein fremder
Host, kein Cookie. Geprüft: die einzigen Subressourcen sind `/styles.css` und ein
`data:`-Favicon. Beide externen Links sind Anker, keine Requests.

**Wer hier etwas ergänzt, prüft danach:**

```bash
grep -nE '<(link|script|img|iframe|source)' *.html   # nur /styles.css, data: und rel=canonical erlaubt
grep -n 'style="' *.html                             # muss leer bleiben
grep -nE '@import|url\(' styles.css                  # muss leer bleiben
```

Eine eingebundene Webfont-URL oder ein Analytics-Snippet macht die Aussage im Footer und
in der Datenschutzerklärung zur Lüge — und die CSP blockt es ohnehin.

## Vor dem Livegang zu füllen

Impressums- und Firmendaten sind aus `sitelook.de/impressum/` übernommen (Stand 25.08.2026):
Firma, Anschrift, HRB 9239 / AG Neuss, USt-ID, Geschäftsführung, Telefon, `info@sitelook.gmbh`.

Offen bleibt:

| Punkt | Datei | Was |
|---|---|---|
| Kontaktadresse | `index.html`, Impressum | derzeit `info@sitelook.gmbh`. Eine Adresse `…@wirkarchitektur.de` braucht MX-Einträge |
| Hoster-Entität | `datenschutz.html` | beim Anlegen des Cloudflare-Kontos genaue Vertragsentität und AVV-Link gegenprüfen |

## Deploy (Cloudflare Pages)

1. Cloudflare → **Workers & Pages** → *Create* → *Pages* → *Connect to Git* →
   Repo `sitelookgmbh-arch/wirkarchitektur-site`.
2. Build settings: **Framework preset: None** · **Build command: leer** ·
   **Build output directory: `/`**. Kein Build — die Dateien werden nur verteilt.
3. Nach dem ersten Deploy: *Custom domains* → `wirkarchitektur.de` hinzufügen.
   Voraussetzung: Die Zone liegt bei Cloudflare (Nameserver bei Strato umstellen).
4. `_headers` greift automatisch. `_redirects` enthält bewusst nichts.

### Domainweiterleitungen — NICHT über `_redirects`

Cloudflare Pages unterstützt in `_redirects` **keine** domainübergreifenden
Weiterleitungen. Für `wirkarchitektur.com`, `digitale-wirkarchitektur.de` und `www.`:

- Zone in Cloudflare anlegen (Nameserver umstellen).
- Proxied DNS-Eintrag setzen, damit Anfragen überhaupt bei Cloudflare landen —
  z. B. `AAAA @ 100::` (Discard-Adresse), orange Wolke an. Ohne proxied Record
  greift keine Regel.
- **Rules → Redirect Rules → Single Redirect**:
  *When* `hostname eq "wirkarchitektur.com"` → *Then* dynamic redirect,
  `concat("https://wirkarchitektur.de", http.request.uri.path)`, Status **301**,
  Query-String erhalten.
- Für `digitale-wirkarchitektur.de` und die `www.`-Varianten dasselbe.

### Prüfen nach dem Deploy

```bash
curl -sI https://wirkarchitektur.de/ | grep -i content-security-policy
curl -s -o /dev/null -w '%{http_code}\n' https://wirkarchitektur.de/gibtsnicht     # 404
curl -sI https://wirkarchitektur.com/ | grep -iE '^(HTTP|location)'                # 301
curl -sI https://digitale-wirkarchitektur.de/ | grep -iE '^(HTTP|location)'        # 301
```

## Lizenz

Texte und Gestaltung © sitelook GmbH, alle Rechte vorbehalten. Apache-2.0 gilt für `werkzeuge/`
und für die Methodenauszüge unter `/methode/`, die aus `sitelookgmbh-arch/zfdw-ki-leitplanken`
erzeugt werden. Einzelheiten: [LICENSE.md](LICENSE.md). „Wirkarchitektur“ und „sitelook“ sind
angemeldete Wortmarken der sitelook GmbH; die Apache-Lizenz erteilt daran keine Rechte.

**E-Mail-Adressen** stehen in `<!--email_off-->…<!--/email_off-->`: Cloudflares
E-Mail-Verschleierung bräuchte sonst ein Skript, das die CSP (`default-src 'none'`) blockt — die
Adresse wäre im Browser nicht lesbar.

## Methodenseiten (`/methode/`)

Die Seiten unter `methode/` sind **Einstiege, keine Kopien**: Frage, wichtigster Satz,
Kurzfassung, erster Absatz des Problems, Prüfliste und die Abschnittsliste mit Links in den
Volltext. Der Volltext bleibt im Repo `zfdw-ki-leitplanken` — eine Regel steht an genau einer
Stelle.

Erzeugt werden sie von `werkzeuge/methodenseiten.py` aus einem lokalen Checkout des
Methoden-Repos (Standard: `../zfdw-ki-leitplanken`). Kein Build beim Ausliefern: Das Skript
schreibt statisches HTML, das wie jede andere Datei committet wird.

```bash
werkzeuge/methodenseiten.py             # nach Änderungen im Methoden-Repo: neu erzeugen, Diff lesen
werkzeuge/methodenseiten.py --pruefen   # Exit 1, wenn eine Seite nicht mehr zum Repo passt
python3 werkzeuge/test_methodenseiten.py  # nach Änderungen am Generator
```

`--pruefen` ist der Rot-Beweis gegen Drift: Er vergleicht jede Seite und den Sitemap-Block mit
dem, was das Repo heute ergäbe — auch verwaiste Seiten zu gelöschten Methoden.

Beides läuft in CI (`.github/workflows/tests.yml`) bei jedem PR und jedem Push auf `main`, gegen
`zfdw-ki-leitplanken` `main`. Ändert sich dort eine Methode, wird die Site-CI rot, bis die Seiten
neu erzeugt sind — auch auf einem PR, der damit nichts zu tun hat.

Die Prüfliste ist der Abschnitt, dessen Überschrift mit „Prüfen“ beginnt (`## Prüfen` oder eine
Langform wie `## Prüfen, ob es eingehalten wurde`). Übernommen wird jeder Punkt darunter
vollständig, auch wenn er im Methodentext über mehrere eingerückte Zeilen umbricht. Eine verschachtelte Liste unter einem Prüfpunkt kann die Seite
nicht abbilden; dann bricht das Skript ab, statt still zu kürzen.

## Herkunfts-Gate

Die Site ist öffentlich und zitiert Methodentexte. Vor jedem PR:

```bash
ln -s ../zfdw-ki-leitplanken/.herkunft-begriffe .herkunft-begriffe   # einmalig
werkzeuge/herkunft-check.sh                                            # 0 = kein Treffer
```

Das Skript ruft das Gate aus `zfdw-ki-leitplanken` auf, mit **derselben** Begriffsliste. Es gibt
also nur eine Liste und nur eine Logik. Fehlt `.herkunft-begriffe` oder ist sie leer, bricht es mit
Exit 2 ab: Ein Lauf ohne Begriffe dieses Projekts wäre grün, aber ohne Aussage. Die Datei enthält
Kunden-, System- und Personennamen. Sie steht in `.gitignore`, und das Skript verweigert den Lauf,
wenn sie versioniert ist. Ein leeres Ergebnis ist die untere Schranke, keine Freigabe: Die Belege
liest trotzdem ein Mensch.

## Zahlen der Startseite

Testfälle, Nicht-Treffer und Mutanten auf `index.html` stammen aus `zfdw-ki-leitplanken`, die
Größen im Kolophon aus den ausgelieferten Dateien. `werkzeuge/zahlen-check.sh` führt Guard-Suite und
Rot-Beweis aus und vergleicht alles mit der Seite (Exit 1 bei Abweichung); in CI als Job `zahlen`,
zusammen mit seinem Rot-Beweis `werkzeuge/test_zahlen-check.sh`. Gemessen wird wie ausgeliefert:
ohne die `email_off`-Marker, die Cloudflare entfernt, in Dezimal-kB mit einer Nachkommastelle.

Wer HTML oder CSS ändert, lässt den Check danach laufen und zieht das Kolophon nach. Wer
`styles.css` ändert, setzt außerdem das Datum in `styles.css?v=…` in allen HTML-Dateien und in
`werkzeuge/methodenseiten.py` neu (ein Jahr `immutable` im Cache, siehe `_headers`).

