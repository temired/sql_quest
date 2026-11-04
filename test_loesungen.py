"""
Selbsttest: Prüft, dass jede Musterlösung von der Engine akzeptiert wird,
nicht leer ist und dass "nichts tun" NICHT als richtig durchgeht.
Start: python test_loesungen.py
"""
import sys

from engine import pruefe_aufgabe, ausfuehren, neue_db
from kapitel import ALLE_KAPITEL


def alle_aufgaben():
    for k in ALLE_KAPITEL:
        for li, lek in enumerate(k["lektionen"], 1):
            for ai, a in enumerate(lek["aufgaben"], 1):
                yield f"{k['nr']}.{li}.{ai}", a
        if k.get("boss"):
            yield f"{k['nr']}.B", k["boss"]


def main():
    fehler, anzahl = [], 0
    for aid, a in alle_aufgaben():
        anzahl += 1
        typ = a.get("typ", "abfrage")
        if typ == "quiz":
            if not 1 <= a["richtig"] <= len(a["optionen"]):
                fehler.append(f"{aid}: 'richtig' außerhalb der Optionen")
            continue
        ok, msg, ausgabe = pruefe_aufgabe(a, a["loesung"])
        if not ok:
            fehler.append(f"{aid}: Musterlösung wird abgelehnt: {msg}\n{ausgabe}")
            continue
        if typ == "abfrage":
            erg = ausfuehren(neue_db(a.get("setup")), a["loesung"])
            if not erg.zeilen and not a.get("leer_ok"):
                fehler.append(f"{aid}: Musterlösung liefert 0 Zeilen")
        else:
            ok_noop, _, _ = pruefe_aufgabe(a, "SELECT 1;")
            if ok_noop:
                fehler.append(f"{aid}: 'Nichts tun' wird als richtig gewertet")
        for falsch in a.get("falsch", []):
            ok_f, _, _ = pruefe_aufgabe(a, falsch)
            if ok_f:
                fehler.append(f"{aid}: Falsche Antwort wird akzeptiert: {falsch}")
        for richtig in a.get("auch_richtig", []):
            ok_r, msg_r, aus_r = pruefe_aufgabe(a, richtig)
            if not ok_r:
                fehler.append(f"{aid}: Alternative Lösung wird abgelehnt: {richtig}\n  {msg_r}\n{aus_r}")
    print(f"{anzahl} Aufgaben geprüft.")
    for f in fehler:
        print("FEHLER", f)
    print("Alles OK" if not fehler else f"{len(fehler)} Fehler")
    sys.exit(1 if fehler else 0)


if __name__ == "__main__":
    main()
