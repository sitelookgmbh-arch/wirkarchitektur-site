#!/usr/bin/env bash
# herkunft-check.sh — Herkunfts-Gate fuer wirkarchitektur.de
#
# Duenner Aufrufer: Das Gate selbst und seine Logik stehen an genau einer Stelle,
# in zfdw-ki-leitplanken/werkzeuge/herkunft-check.sh (wie methodenseiten.py
# braucht es den lokalen Checkout daneben). Hier kommt nur eine Bedingung dazu:
#
# Ohne .herkunft-begriffe nimmt das Gate dort seine Vorlage, und die enthaelt
# keinen einzigen Begriff dieses Projekts — ein Lauf damit hat keine Aussage.
# Deshalb bricht dieser Aufrufer ab, wenn die Begriffsdatei fehlt oder leer ist,
# statt sich auf das Verhalten der Vorlage zu verlassen.
#
# Begriffsliste: dieselbe wie in zfdw-ki-leitplanken, einmal verlinkt:
#   ln -s ../zfdw-ki-leitplanken/.herkunft-begriffe .herkunft-begriffe
# Sie enthaelt Kunden-, System- und Personennamen, ist per .gitignore
# ausgeschlossen und gehoert NIE in dieses oeffentliche Repo.
#
# Aufruf:  werkzeuge/herkunft-check.sh [PFAD-ZUM-METHODEN-REPO]
#          Standard: ../zfdw-ki-leitplanken
# Rueckgabe: 0 = kein Treffer, 1 = Treffer, 2 = Gate nicht scharf (keine Aussage).

set -uo pipefail
site="$(cd "$(dirname "$0")/.." && pwd)"
methoden="${1:-$site/../zfdw-ki-leitplanken}"
gate="$methoden/werkzeuge/herkunft-check.sh"
cd "$site" || exit 2

if [ ! -x "$gate" ]; then
  echo "Abbruch: Herkunfts-Gate nicht gefunden: $gate" >&2
  echo "Erwartet wird ein Checkout von zfdw-ki-leitplanken neben diesem Repo." >&2
  exit 2
fi
if [ ! -s .herkunft-begriffe ]; then
  echo "Abbruch: .herkunft-begriffe fehlt oder ist leer — ohne sie hat das Gate keine" >&2
  echo "Begriffe dieses Projekts und damit keine Aussage. Einmal anlegen:" >&2
  echo "  ln -s ../zfdw-ki-leitplanken/.herkunft-begriffe .herkunft-begriffe" >&2
  exit 2
fi
if git ls-files --error-unmatch .herkunft-begriffe >/dev/null 2>&1; then
  echo "Abbruch: .herkunft-begriffe ist versioniert — sie gehoert nie in dieses Repo." >&2
  exit 1
fi

exec "$gate" .
