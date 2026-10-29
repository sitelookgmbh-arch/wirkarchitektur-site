#!/usr/bin/env bash
# Sammelt öffentliche Änderungsnotizen; kein Commit, Push oder Tag.
set -euo pipefail
export LC_ALL=C
fail() { printf '%s\n' "$*" >&2; exit 1; }
version='' dry=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) dry=1 ;;
    *) [ -z "$version" ] || fail 'Genau eine Version erforderlich'; version=$arg ;;
  esac
done
[[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || fail 'Version X.Y.Z erforderlich'
cd -P "$(dirname "$0")/.."
[ "$(git rev-parse --show-toplevel)" = "$PWD" ] || fail 'Repo-Wurzel erforderlich'
branch=$(git symbolic-ref --quiet --short HEAD) || fail 'Arbeitsbranch erforderlich'
case "$branch" in main|master) fail 'Eigener Arbeitsbranch erforderlich' ;; esac
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail 'Arbeitsbaum nicht sauber'
[ -f CHANGELOG.md ] && [ ! -L CHANGELOG.md ] || fail 'Reguläres CHANGELOG.md erforderlich'
[ -d changelog.d ] && [ ! -L changelog.d ] || fail 'Reguläres changelog.d erforderlich'
[ "$(grep -c '^## \[Unreleased\]$' CHANGELOG.md)" = 1 ] || fail 'Eindeutiger Unreleased-Abschnitt erforderlich'
! grep -Fq "## [$version]" CHANGELOG.md || fail 'Version bereits vorhanden'
[ ! -L changelog.d/archive ] || fail 'Archiv darf kein Symlink sein'
[ ! -e "changelog.d/archive/$version" ] && [ ! -L "changelog.d/archive/$version" ] || fail 'Archivziel bereits vorhanden'
shopt -s nullglob
files=()
for file in changelog.d/*.md; do
  [ "$file" = changelog.d/README.md ] && continue
  [[ "${file##*/}" =~ ^[a-z0-9][a-z0-9-]*\.md$ ]] || fail 'Ungültiger Fragmentname'
  [ -f "$file" ] && [ ! -L "$file" ] || fail 'Fragment muss reguläre Datei sein'
  files+=("$file")
done
[ "${#files[@]}" -gt 0 ] || fail 'Keine offenen Fragmente'
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
for file in "${files[@]}"; do
  section=$(head -n 1 "$file")
  case "$section" in Added|Changed|Fixed|Security) ;; *) fail "Ungültiger Abschnitt: $file" ;; esac
  # Mindestens ein Listenpunkt; Fortsetzungen müssen eingerückt sein.
  awk 'NR == 1 {next} /^- .+/ {entries++; next} /^$/ {next}
       /^  +[^ ]/ {if (entries) next} {exit 1}
       END {if (!entries) exit 1}' "$file" || fail "Ungültiger Inhalt: $file"
  tail -n +2 "$file" >> "$tmp/$section"
  printf '\n' >> "$tmp/$section"
done
{
  printf '## [%s] - %s\n' "$version" "$(date +%F)"
  for section in Added Changed Fixed Security; do
    if [ -f "$tmp/$section" ]; then
      printf '\n### %s\n' "$section"
      cat "$tmp/$section"
    fi
  done
} > "$tmp/block"
# Bestehenden Unreleased-Inhalt unverändert lassen; vor erster älterer Version einfügen.
awk -v block="$tmp/block" '
  function insert( line) {while ((getline line < block) > 0) print line; close(block)}
  /^## \[Unreleased\]$/ {seen=1; print; next}
  seen && /^## / && !done {insert(); print ""; done=1}
  {print}
  END {if (!done) {print ""; insert()}}
' CHANGELOG.md > "$tmp/CHANGELOG.md"
if [ "$dry" -eq 1 ]; then
  cat "$tmp/block"
  printf '\nArchiv: changelog.d/archive/%s/\n' "$version"
  exit 0
fi
mkdir -p "changelog.d/archive/$version"
for file in "${files[@]}"; do mv "$file" "changelog.d/archive/$version/"; done
cat "$tmp/CHANGELOG.md" > CHANGELOG.md
printf 'Gesammelt: %s (%s Fragmente)\n' "$version" "${#files[@]}"
