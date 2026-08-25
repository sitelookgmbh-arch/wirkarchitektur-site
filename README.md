# wirkarchitektur.de

Statische Seite. Handgeschriebenes HTML, ein Stylesheet, **kein Build**, keine
Dependencies. Deploy = Dateien hochladen.

```
index.html        Startseite
impressum.html    § 5 DDG  — Platzhalter, s. u.
datenschutz.html  DSGVO    — Platzhalter, s. u.
404.html          ehrlicher 404 statt Weiterleitung
styles.css        das einzige Stylesheet
_headers          CSP + Security-Header (Cloudflare Pages)
_redirects        .com und Langform -> wirkarchitektur.de
robots.txt · sitemap.xml
```

## Die Zusage der Seite

`default-src 'none'` in `/_headers`. Kein Skript, keine externe Schriftart, kein fremder
Host, kein Cookie. Geprüft: die einzigen Subressourcen sind `/styles.css` und ein
`data:`-Favicon. Beide externen Links sind Anker, keine Requests.

**Wer hier etwas ergänzt, prüft danach:**

```bash
grep -nE '<(link|script|img|iframe|source)' *.html   # nur /styles.css + data: erlaubt
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

1. Repo bei GitHub anlegen, diesen Ordner pushen.
2. Cloudflare → Workers & Pages → *Create* → *Pages* → Git-Repo verbinden.
3. Build command: **leer**. Output directory: **`/`**. Framework: **None**.
4. Custom domain `wirkarchitektur.de` hinzufügen (Nameserver der Zone müssen bei
   Cloudflare liegen).
5. `_headers` und `_redirects` greifen automatisch — nichts zu konfigurieren.

Prüfen nach dem Deploy:

```bash
curl -sI https://wirkarchitektur.de/ | grep -i content-security-policy
curl -s -o /dev/null -w '%{http_code}\n' https://wirkarchitektur.de/gibtsnicht   # 404
curl -s -o /dev/null -w '%{redirect_url}\n' https://digitale-wirkarchitektur.de/
```

## Lizenz

Inhalte © sitelook GmbH. Der Code der Methode, auf die die Seite verweist, liegt unter
Apache-2.0 in `sitelookgmbh-arch/zfdw-ki-leitplanken`.
