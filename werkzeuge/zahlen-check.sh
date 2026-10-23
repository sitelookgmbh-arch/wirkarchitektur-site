#!/usr/bin/env bash
# zahlen-check.sh — Die Zahlen auf index.html gegen einen echten Lauf pruefen
#
# Die Startseite nennt Zahlen, die anderswo entstehen: Testfaelle und
# Nicht-Treffer der Guard-Suite, Mutanten des Rot-Beweises (beides in
# zfdw-ki-leitplanken) und die Groesse von HTML und CSS im Kolophon. Ohne
# Pruefung laufen sie still auseinander — genau der Spec Drift, den die Seite
# beschreibt (Methode 05: jede Angabe braucht die Zeile, mit der man sie prueft).
#
# Gemessen wird:
#   - hooks/tests/test-guard.sh: "N bestanden, 0 fehlgeschlagen" und die Zahl der
#     Faelle mit erwartetem Code 0 (die bewussten Nicht-Treffer)
#   - hooks/tests/rot-beweis.sh: "N erkannt, 0 blind"
#   - index.html und styles.css in Bytes, wie Cloudflare sie ausliefert: ohne die
#     Marker <!--email_off--> und <!--/email_off-->, die Cloudflare entfernt.
#     Angabe auf der Seite: Dezimal-kB mit einer Nachkommastelle (21156 B = 21,2 kB).
#
# Aufruf:  werkzeuge/zahlen-check.sh [PFAD-ZUM-METHODEN-REPO]
#          Standard: ../zfdw-ki-leitplanken
#   --html DATEI       andere HTML-Datei pruefen (fuer den Rot-Beweis)
#   --ist "T N M"      Testfaelle, Nicht-Treffer, Mutanten vorgeben statt messen
#                      (nur fuer den Rot-Beweis, damit er die Suite nicht dreimal laeuft)
# Rueckgabe: 0 = alles stimmt, 1 = Abweichung, 2 = Messung nicht moeglich.

set -uo pipefail
site="$(cd "$(dirname "$0")/.." && pwd)"
methoden="" html="$site/index.html" ist=""
while [ $# -gt 0 ]; do
  case "$1" in
    --html) html="$2"; shift 2 ;;
    --ist)  ist="$2"; shift 2 ;;
    *)      methoden="$1"; shift ;;
  esac
done
methoden="${methoden:-$site/../zfdw-ki-leitplanken}"
fehler=0

if [ -n "$ist" ]; then
  read -r tests nicht mutanten <<<"$ist"
else
  suite="$methoden/hooks/tests/test-guard.sh"
  rot="$methoden/hooks/tests/rot-beweis.sh"
  if [ ! -x "$suite" ] || [ ! -x "$rot" ]; then
    echo "Abbruch: Testsuite nicht gefunden unter $methoden/hooks/tests" >&2
    exit 2
  fi
  aus=$("$suite" 2>&1) || { echo "Abbruch: Guard-Suite ist rot, keine Aussage." >&2; exit 2; }
  tests=$(printf '%s\n' "$aus" | sed -n 's/^\([0-9][0-9]*\) bestanden, 0 fehlgeschlagen$/\1/p')
  nicht=$(printf '%s\n' "$aus" | grep -cE '^  ok .*\(Code 0\)$')
  aus=$("$rot" 2>&1) || { echo "Abbruch: Rot-Beweis ist rot, keine Aussage." >&2; exit 2; }
  mutanten=$(printf '%s\n' "$aus" | sed -n 's/^\([0-9][0-9]*\) erkannt, 0 blind$/\1/p')
  if [ -z "$tests" ] || [ -z "$mutanten" ]; then
    echo "Abbruch: Schlusszeile der Suite oder des Rot-Beweises nicht lesbar." >&2
    exit 2
  fi
fi

# Ausgelieferte Groesse in Dezimal-kB mit Komma
kb() { python3 -c 'import sys; b=open(sys.argv[1],"rb").read(); b=b.replace(b"<!--email_off-->",b"").replace(b"<!--/email_off-->",b""); print(f"{len(b)/1000:.1f}".replace(".",","))' "$1"; }
html_kb=$(kb "$site/index.html")
css_kb=$(kb "$site/styles.css")

vergleiche() {  # Bezeichnung, Ist, Seite
  if [ "$2" = "$3" ]; then
    printf '  ok      %-28s %s\n' "$1" "$2"
  else
    printf '  FALSCH  %-28s Seite: %s, gemessen: %s\n' "$1" "${3:-(fehlt)}" "$2"
    fehler=1
  fi
}

seite() { grep -oE "$1" "$html" | head -1 | grep -oE '[0-9]+(,[0-9])?' | sed -n "${2:-1}p"; }

echo "Zahlen auf $(basename "$html") gegen die Messung:"
vergleiche "Testfaelle"            "$tests"    "$(seite '[0-9]+ Testfälle')"
vergleiche "bewusste Nicht-Treffer" "$nicht"   "$(seite 'davon [0-9]+ bewusste Nicht-Treffer')"
vergleiche "Beispielausgabe"       "$tests"    "$(seite '[0-9]+ bestanden, 0 fehlgeschlagen')"
vergleiche "Mutanten"              "$mutanten" "$(seite 'baut [0-9]+ absichtlich')"
vergleiche "HTML (kB)"             "$html_kb"  "$(seite '<strong>[0-9]+,[0-9] kB</strong> HTML')"
vergleiche "CSS (kB)"              "$css_kb"   "$(seite '<strong>[0-9]+,[0-9] kB</strong> CSS')"

exit $fehler
