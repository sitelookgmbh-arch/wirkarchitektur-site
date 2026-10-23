#!/usr/bin/env bash
# Rot-Beweis fuer zahlen-check.sh
#
# Ein Check, der gruen ist, beweist nur etwas, wenn er auch rot werden kann.
# Dieses Skript verfaelscht je eine Zahl in einer Kopie von index.html und
# verlangt, dass zahlen-check.sh jede Verfaelschung bemerkt. Die Ist-Zahlen
# kommen per --ist aus der unveraenderten Seite; ob die selbst stimmt, prueft
# der eigentliche Lauf von zahlen-check.sh (in CI direkt davor).
#
# Aufruf:  werkzeuge/test_zahlen-check.sh
# Rueckgabe: 0 = jede Verfaelschung erkannt, 1 = blinder Fleck.

set -uo pipefail
site="$(cd "$(dirname "$0")/.." && pwd)"
check="$site/werkzeuge/zahlen-check.sh"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

zahl() { grep -oE "$1" "$site/index.html" | head -1 | grep -oE '[0-9]+' | head -1; }
ist="$(zahl '[0-9]+ Testfälle') $(zahl 'davon [0-9]+ bewusste') $(zahl 'baut [0-9]+ absichtlich')"
fehler=0

fall() {  # Bezeichnung, erwarteter Code, sed-Ausdruck
  cp "$site/index.html" "$tmp/index.html"
  [ -n "$3" ] && sed -i.bak -E "$3" "$tmp/index.html"
  "$check" --html "$tmp/index.html" --ist "$ist" >/dev/null 2>&1; code=$?
  if [ "$code" = "$2" ]; then
    printf '  ok    %-34s (Code %s)\n' "$1" "$code"
  else
    printf '  FEHL  %-34s (Code %s, erwartet %s)\n' "$1" "$code" "$2"
    fehler=1
  fi
}

echo "Gegenprobe:"
fall "unveraenderte Seite"                 0 ""
echo "Verfaelschungen (muessen rot werden):"
fall "Testfaelle falsch"                   1 's/[0-9]+ Testfälle/1 Testfälle/'
fall "Nicht-Treffer falsch"                1 's/davon [0-9]+ bewusste/davon 1 bewusste/'
fall "Beispielausgabe falsch"              1 's/[0-9]+ bestanden, 0 fehlgeschlagen/1 bestanden, 0 fehlgeschlagen/'
fall "Mutanten falsch"                     1 's/baut [0-9]+ absichtlich/baut 1 absichtlich/'
fall "HTML-Groesse falsch"                 1 's#<strong>[0-9]+,[0-9] kB</strong> HTML#<strong>0,1 kB</strong> HTML#'
fall "CSS-Groesse falsch"                  1 's#<strong>[0-9]+,[0-9] kB</strong> CSS#<strong>0,1 kB</strong> CSS#'
fall "Zahl fehlt ganz"                     1 's/[0-9]+ Testfälle/viele Testfälle/'

exit $fehler
