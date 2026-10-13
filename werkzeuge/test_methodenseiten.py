#!/usr/bin/env python3
"""Tests fuer methodenseiten.py: Pruefliste (mehrzeilige Punkte, Form der Ueberschrift).

Aufruf:  python3 werkzeuge/test_methodenseiten.py
Nur Standardbibliothek, synthetische Methode, kein Checkout von zfdw-ki-leitplanken noetig.
"""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import methodenseiten  # noqa: E402

KOPF = """# 99 — Beispielmethode

> **Kurz:** Eine Methode nur für den Test.

## Das Problem

Ein Absatz.

"""


def methode(pruefen_block, ueberschrift="## Prüfen"):
    with tempfile.TemporaryDirectory() as d:
        datei = pathlib.Path(d) / "99_Beispiel.md"
        datei.write_text(KOPF + ueberschrift + "\n" + pruefen_block, encoding="utf-8")
        return datei.name, methodenseiten.lies_methode(datei)


def lies(pruefen_block, ueberschrift="## Prüfen"):
    return methode(pruefen_block, ueberschrift)[1]["pruefen"]


class Pruefliste(unittest.TestCase):
    def test_einzeilige_punkte(self):
        self.assertEqual(lies("\n- [ ] Erster Punkt.\n- [ ] Zweiter Punkt.\n"),
                         ["Erster Punkt.", "Zweiter Punkt."])

    def test_mehrzeiliger_punkt_vollstaendig(self):
        block = ("\n- [ ] Kann man nach dem Lesen **einer** Datei sagen, wozu es da ist — ohne den\n"
                 "      Code zu öffnen?\n"
                 "- [ ] Danach ein einzeiliger Punkt.\n")
        self.assertEqual(lies(block), [
            "Kann man nach dem Lesen **einer** Datei sagen, wozu es da ist — ohne den Code zu öffnen?",
            "Danach ein einzeiliger Punkt.",
        ])

    def test_drei_zeilen_und_tab(self):
        block = "\n- [ ] eins\n  zwei\n\tdrei\n"
        self.assertEqual(lies(block), ["eins zwei drei"])

    def test_leerzeile_und_trenner_beenden_den_punkt(self):
        block = ("\n- [ ] Letzter Punkt, der hier\n      endet.\n\n---\n\n"
                 "**Herleitung.** Ein Absatz, der nicht in die Liste gehört.\n")
        self.assertEqual(lies(block), ["Letzter Punkt, der hier endet."])

    def test_eingerueckter_text_ohne_punkt_davor_wird_nicht_angehaengt(self):
        block = "\n    eingerückt, aber kein Punkt davor\n- [ ] Einziger Punkt.\n"
        self.assertEqual(lies(block), ["Einziger Punkt."])

    def test_verschachtelte_liste_bricht_ab(self):
        block = "\n- [ ] Oberpunkt\n  - Unterpunkt\n"
        with self.assertRaises(SystemExit) as fehler:
            lies(block)
        self.assertIn("verschachtelte Liste", str(fehler.exception.code))

    def test_html_zeigt_den_ganzen_punkt(self):
        punkte = lies("\n- [ ] Anfang des Punkts —\n      Ende des Punkts?\n")
        html = methodenseiten.inline(punkte[0])
        self.assertIn("Anfang des Punkts — Ende des Punkts?", html)



class Ueberschrift(unittest.TestCase):
    LANGFORM = "## Prüfen, ob es eingehalten wurde"
    BLOCK = "\n- [ ] Erster Punkt.\n- [ ] Zweiter Punkt.\n\n## Verwandt\n\n- [ ] kein Prüfpunkt mehr\n"

    def test_langform_wird_erkannt(self):
        self.assertEqual(lies(self.BLOCK, self.LANGFORM), ["Erster Punkt.", "Zweiter Punkt."])

    def test_wort_mit_praefix_ist_keine_pruefliste(self):
        self.assertEqual(lies(self.BLOCK, "## Prüfenswerte Fälle"), [])

    def test_langform_steht_als_pruefliste_nicht_in_der_abschnittsliste(self):
        name, m = methode(self.BLOCK, self.LANGFORM)
        _, seite = methodenseiten.methodenseite(
            "99", 99, {"frage": "Frage?", "satz": "Satz."}, m, pathlib.Path(name),
            "2026-01-01", None, None)
        self.assertIn("<h2>Prüfliste</h2>", seite)
        self.assertIn("<li>Erster Punkt.</li>", seite)
        self.assertNotIn("#prüfen-ob-es-eingehalten-wurde", seite)
        self.assertIn("#verwandt", seite)


if __name__ == "__main__":
    unittest.main(verbosity=2)
