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
| Strato-Vertrag | — | prüfen, ob die Domains auf der GmbH oder privat laufen (Bestellbestätigung lautete auf die Geschäftsführerin) |

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

Inhalte © sitelook GmbH. Der Code der Methode, auf die die Seite verweist, liegt unter
Apache-2.0 in `sitelookgmbh-arch/zfdw-ki-leitplanken`.

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
```

`--pruefen` ist der Rot-Beweis gegen Drift: Er vergleicht jede Seite und den Sitemap-Block mit
dem, was das Repo heute ergäbe — auch verwaiste Seiten zu gelöschten Methoden.
