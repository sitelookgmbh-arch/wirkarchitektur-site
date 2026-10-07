#!/usr/bin/env python3
"""Methodenseiten fuer wirkarchitektur.de aus zfdw-ki-leitplanken erzeugen und pruefen.

Kein Build-Schritt der Seite: Das Skript schreibt statisches HTML, das wie jede andere
Datei committet wird. Ausgeliefert wird weiter nur, was im Repo liegt.

Die Seiten sind Einstiege, keine Kopien. Uebernommen werden nur die Teile, die in jeder
Methode dieselbe Form haben — Frage, wichtigster Satz, Kurzfassung, erster Absatz des
Problems, Pruefliste, Abschnittsliste. Der Volltext bleibt im Repo, eine Regel steht an
genau einer Stelle.

Aufruf:
  werkzeuge/methodenseiten.py [PFAD-ZUM-REPO]            Seiten + Sitemap-Block schreiben
  werkzeuge/methodenseiten.py --pruefen [PFAD-ZUM-REPO]  Exit 1, wenn eine Seite nicht
                                                         mehr zum Repo passt (Drift)

PFAD-ZUM-REPO: lokaler Checkout von zfdw-ki-leitplanken, Standard ../zfdw-ki-leitplanken.
Nur Standardbibliothek.
"""
import html
import pathlib
import re
import subprocess
import sys

SITE = pathlib.Path(__file__).resolve().parent.parent
BASIS = "https://wirkarchitektur.de"
GITHUB = "https://github.com/sitelookgmbh-arch/zfdw-ki-leitplanken/blob/main/"
SITEMAP_START = "  <!-- methode:start (erzeugt von werkzeuge/methodenseiten.py) -->"
SITEMAP_ENDE = "  <!-- methode:end -->"


# ---------- Markdown, nur das Noetigste ----------

def slug_github(text):
    """Anker so, wie GitHub ihn aus einer Ueberschrift bildet."""
    s = text.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s, flags=re.UNICODE)
    return s.replace(" ", "-")


def seiten_slug(dateiname):
    return pathlib.Path(dateiname).stem.lower().replace("_", "-")


def link_ziel(ziel, quelle_dir):
    """Relativen Repo-Link auf eine Methodenseite oder auf GitHub abbilden."""
    if ziel.startswith(("http://", "https://", "mailto:")):
        return ziel
    pfad, _, anker = ziel.partition("#")
    if pfad == "" and anker:
        return "#" + anker
    aufgeloest = (pathlib.PurePosixPath(quelle_dir) / pfad).as_posix()
    teile = []
    for t in aufgeloest.split("/"):
        if t == "..":
            if teile:
                teile.pop()
        elif t not in ("", "."):
            teile.append(t)
    aufgeloest = "/".join(teile)
    if re.fullmatch(r"methode/\d\d_[^/]+\.md", aufgeloest) and not anker:
        return "/methode/" + seiten_slug(aufgeloest)
    return GITHUB + aufgeloest + ("#" + anker if anker else "")


def inline(text, quelle_dir="methode"):
    """Inline-Markdown -> HTML: Code, Links, fett, kursiv. Alles andere wird escaped."""
    platzhalter = []

    def merke(fragment):
        platzhalter.append(fragment)
        return f"\x00{len(platzhalter) - 1}\x00"

    text = re.sub(r"`([^`]+)`", lambda m: merke("<code>" + html.escape(m.group(1)) + "</code>"), text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: merke(f'<a href="{html.escape(link_ziel(m.group(2), quelle_dir))}">')
        + m.group(1) + merke("</a>"),
        text,
    )
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: platzhalter[int(m.group(1))], text)


def klartext(text):
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.replace("**", "").replace("`", "")
    return re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", text)


def kuerzen(text, laenge=155):
    if len(text) <= laenge:
        return text
    return text[: laenge - 1].rsplit(" ", 1)[0] + " …"


# ---------- Quellen lesen ----------

def lies_index(repo):
    """Tabelle und Reihenfolge-Abschnitt aus methode/README.md."""
    zeilen = (repo / "methode" / "README.md").read_text(encoding="utf-8").splitlines()
    eintraege = {}
    for z in zeilen:
        m = re.match(r"\| \[(\d\d) — ([^\]]+)\]\(([^)]+)\) \| (.+?) \| (.+?) \|$", z)
        if m:
            eintraege[m.group(3)] = {"nr": m.group(1), "kurztitel": m.group(2),
                                     "frage": m.group(4), "satz": m.group(5)}
    reihenfolge = []
    if "## Reihenfolge" in zeilen:
        absatz = []
        for z in zeilen[zeilen.index("## Reihenfolge") + 1:]:
            if z.startswith("## "):
                break
            if z.strip():
                absatz.append(z.strip())
            elif absatz:
                reihenfolge.append(" ".join(absatz)); absatz = []
        if absatz:
            reihenfolge.append(" ".join(absatz))
    return eintraege, reihenfolge


def lies_methode(datei):
    zeilen = datei.read_text(encoding="utf-8").splitlines()
    titel = zeilen[0].lstrip("# ").strip()
    kurz, i = [], 1
    while i < len(zeilen) and not zeilen[i].startswith("> **Kurz:**"):
        i += 1
    while i < len(zeilen) and zeilen[i].startswith(">"):
        kurz.append(zeilen[i].lstrip("> ").strip()); i += 1
    kurz = " ".join(kurz).replace("**Kurz:** ", "", 1)

    abschnitte = [z[3:].strip() for z in zeilen if z.startswith("## ")]

    # Erster Absatz unter der ersten H2.
    erste = next(k for k, z in enumerate(zeilen) if z.startswith("## "))
    absatz, k = [], erste + 1
    while k < len(zeilen) and not zeilen[k].strip():
        k += 1
    while k < len(zeilen) and zeilen[k].strip() and not zeilen[k].startswith(("#", "-", "|", "```", ">")):
        absatz.append(zeilen[k].strip()); k += 1

    pruefen = []
    if "## Prüfen" in zeilen:
        for z in zeilen[zeilen.index("## Prüfen") + 1:]:
            if z.startswith("## "):
                break
            m = re.match(r"- \[ \] (.+)", z)
            if m:
                pruefen.append(m.group(1))
    return {"titel": titel, "kurz": kurz, "abschnitte": abschnitte,
            "problem_titel": zeilen[erste][3:].strip(), "problem": " ".join(absatz),
            "pruefen": pruefen}


def stand(repo, datei):
    return subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%cs", "--", str(datei)],
                          capture_output=True, text=True, check=True).stdout.strip()


# ---------- HTML ----------

def kopf(titel, beschreibung, pfad):
    t, b = html.escape(titel), html.escape(beschreibung)
    return f"""<!doctype html>
<html lang="de">
<!-- Erzeugt von werkzeuge/methodenseiten.py aus zfdw-ki-leitplanken. Nicht von Hand aendern. -->
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{b}">
<link rel="canonical" href="{BASIS}{pfad}">
<meta property="og:type" content="article">
<meta property="og:url" content="{BASIS}{pfad}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{b}">
<meta property="og:locale" content="de_DE">
<link rel="stylesheet" href="/styles.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' fill='%23111'/><path d='M20 25v50M50 25v50M80 25v50M20 50h60' stroke='%23e8623a' stroke-width='9' fill='none'/></svg>">
</head>
<body>

<header class="top">
  <a class="wordmark" href="/">Wirk<span>architektur</span></a>
  <span class="traeger">Werkstatt der <strong>sitelook GmbH</strong></span>
  <nav>
    <a href="/">Start</a>
    <a href="/methode/">Methode</a>
    <a href="https://github.com/sitelookgmbh-arch/zfdw-ki-leitplanken">Repo</a>
  </nav>
</header>

<main>
"""


FUSS = """</main>

<footer>
  <nav class="fusszeile">
    <a href="/">Start</a>
    <a href="/methode/">Methode</a>
    <a href="/impressum">Impressum</a>
    <a href="/datenschutz">Datenschutz</a>
    <a href="https://github.com/sitelookgmbh-arch/zfdw-ki-leitplanken">Repo</a>
  </nav>
  <p class="klein">Wirkarchitektur ist eine angemeldete Marke der sitelook GmbH, Neuss. Inhalte Apache-2.0, ohne Markenrechte.</p>
</footer>

</body>
</html>
"""


def methodenseite(nr, gesamt, idx, m, datei, datum, vor, nach):
    pfad = "/methode/" + seiten_slug(datei.name)
    quelle = GITHUB + "methode/" + datei.name
    teile = [kopf(f"{m['titel']} — Wirkarchitektur", kuerzen(klartext(m["kurz"])), pfad)]
    teile.append(f"""<section class="hero">
  <p class="meta">Methode {nr} von {gesamt:02d} · Stand {datum}</p>
  <h1>{inline(m['titel'])}</h1>
  <p class="lead">{inline(m['kurz'])}</p>
</section>

<section>
  <h2>Die Frage</h2>
  <div>
    <p>{inline(idx['frage'])}</p>
    <p class="callout">{inline(idx['satz'])}</p>
  </div>
</section>
""")
    if m["problem"]:
        teile.append(f"""
<section>
  <h2>{inline(m['problem_titel'])}</h2>
  <p>{inline(m['problem'])}</p>
</section>
""")
    if m["pruefen"]:
        punkte = "\n".join(f"    <li>{inline(p)}</li>" for p in m["pruefen"])
        teile.append(f"""
<section>
  <h2>Prüfliste</h2>
  <ul>
{punkte}
  </ul>
</section>
""")
    abschnitte = "\n".join(
        f'      <li><a href="{quelle}#{slug_github(a)}">{inline(a)}</a></li>' for a in m["abschnitte"] if a != "Prüfen")
    navi = []
    if vor:
        navi.append(f'<a href="/methode/{seiten_slug(vor)}">← vorherige Methode</a>')
    navi.append('<a href="/methode/">Übersicht</a>')
    if nach:
        navi.append(f'<a href="/methode/{seiten_slug(nach)}">nächste Methode →</a>')
    teile.append(f"""
<section>
  <h2>Im Volltext</h2>
  <div>
    <p>Diese Seite ist der Einstieg. Begründungen, Beispiele und Grenzen stehen im Volltext —
    eine Regel steht an genau einer Stelle, und das ist das Repo.</p>
    <ul>
{abschnitte}
    </ul>
    <p class="callout"><a href="{quelle}">Volltext lesen: methode/{datei.name}</a><br>
    Stand {datum} · Apache-2.0 · Fehler oder Gegenbeispiel bitte als Issue im Repo.</p>
    <p class="klein">{" · ".join(navi)}</p>
  </div>
</section>
""")
    teile.append(FUSS)
    return pfad, "".join(teile)


def uebersicht(liste, reihenfolge):
    zeilen = "\n".join(
        f"""      <tr>
        <td class="wb-name"><a href="/methode/{seiten_slug(d.name)}">{idx['nr']} — {inline(idx['kurztitel'])}</a></td>
        <td class="wb-was">{inline(idx['frage'])}<br><strong>{inline(idx['satz'])}</strong></td>
      </tr>""" for d, idx, _ in liste)
    absaetze = "\n".join(f"    <p>{inline(a)}</p>" for a in reihenfolge)
    return "".join([
        kopf("Methode — Wirkarchitektur",
             f"{len(liste)} Methodentexte für Repos, in denen ein KI-Assistent mitschreibt: "
             "Sprint und Write-Scope, Guards, Verifikation, Herkunft, Fremdtext. Apache-2.0.",
             "/methode/"),
        f"""<section class="hero">
  <p class="meta">zfdw-ki-leitplanken · {len(liste)} Methodentexte</p>
  <h1>Methode</h1>
  <p class="lead">Jeder Text beantwortet eine Frage, nennt zuerst das Problem und dann die Regel —
  wer nur die Regel liest, kann sie nicht sinnvoll anpassen. Hier je Methode der Einstieg, der
  Volltext liegt im Repo.</p>
</section>

<section>
  <h2>Übersicht</h2>
  <table class="werkbank">
    <tbody>
{zeilen}
    </tbody>
  </table>
</section>

<section>
  <h2>Reihenfolge</h2>
  <div>
{absaetze}
  </div>
</section>
""",
        FUSS])


# ---------- Ablauf ----------

def erzeuge(repo):
    index, reihenfolge = lies_index(repo)
    dateien = sorted((repo / "methode").glob("[0-9][0-9]_*.md"))
    liste = []
    for d in dateien:
        if d.name not in index:
            sys.exit(f"Abbruch: {d.name} fehlt in der Tabelle von methode/README.md.")
        liste.append((d, index[d.name], lies_methode(d)))
    ausgabe = {}
    for i, (d, idx, m) in enumerate(liste):
        vor = liste[i - 1][0].name if i > 0 else None
        nach = liste[i + 1][0].name if i + 1 < len(liste) else None
        pfad, inhalt = methodenseite(idx["nr"], len(liste), idx, m, d, stand(repo, d), vor, nach)
        ausgabe[SITE / (pfad.lstrip("/") + ".html")] = (pfad, stand(repo, d), inhalt)
    ausgabe[SITE / "methode" / "index.html"] = ("/methode/", max(v[1] for v in ausgabe.values()),
                                                uebersicht(liste, reihenfolge))
    sitemap = "\n".join(f"  <url><loc>{BASIS}{p}</loc><lastmod>{s}</lastmod></url>"
                        for p, s, _ in sorted(ausgabe.values()))
    return ausgabe, sitemap


def sitemap_mit(block):
    alt = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    if SITEMAP_START in alt:
        vorne, rest = alt.split(SITEMAP_START, 1)
        hinten = rest.split(SITEMAP_ENDE, 1)[1]
    else:
        vorne, hinten = alt.split("</urlset>")[0], "\n</urlset>\n"
    return f"{vorne.rstrip()}\n{SITEMAP_START}\n{block}\n{SITEMAP_ENDE}{hinten if hinten.startswith(chr(10)) else chr(10) + hinten}"


def main():
    args = sys.argv[1:]
    pruefen = "--pruefen" in args
    args = [a for a in args if a != "--pruefen"]
    repo = pathlib.Path(args[0] if args else SITE.parent / "zfdw-ki-leitplanken").resolve()
    if not (repo / "methode" / "README.md").exists():
        sys.exit(f"Abbruch: kein zfdw-ki-leitplanken unter {repo}")
    ausgabe, block = erzeuge(repo)
    sitemap_neu = sitemap_mit(block)

    if pruefen:
        abweichend = [str(p.relative_to(SITE)) for p, (_, _, inhalt) in ausgabe.items()
                      if not p.exists() or p.read_text(encoding="utf-8") != inhalt]
        vorhanden = {p for p in (SITE / "methode").glob("*.html")}
        abweichend += [str(p.relative_to(SITE)) + " (verwaist)" for p in vorhanden - set(ausgabe)]
        if (SITE / "sitemap.xml").read_text(encoding="utf-8") != sitemap_neu:
            abweichend.append("sitemap.xml")
        if abweichend:
            print("Drift — diese Dateien passen nicht mehr zum Repo:")
            for a in abweichend:
                print("  " + a)
            print("Beheben: werkzeuge/methodenseiten.py, Diff lesen, committen.")
            sys.exit(1)
        print(f"Methodenseiten passen zum Repo ({len(ausgabe)} Seiten).")
        return

    (SITE / "methode").mkdir(exist_ok=True)
    for p, (_, _, inhalt) in ausgabe.items():
        p.write_text(inhalt, encoding="utf-8")
    (SITE / "sitemap.xml").write_text(sitemap_neu, encoding="utf-8")
    print(f"{len(ausgabe)} Seiten geschrieben, Sitemap aktualisiert.")


if __name__ == "__main__":
    main()
