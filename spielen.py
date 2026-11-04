"""
SQL-Quest – lerne SQL komplett, Kapitel für Kapitel, im Terminal.
Start:  python spielen.py
"""
import os
import re
import sys
import textwrap

from engine import (BASIS, F, farbe, neue_db, ausfuehren, ergebnis_text, schema_text,
                    leere_tabellenliste, pruefe_aufgabe, tabelle_text, erwartet)
from kapitel import ALLE_KAPITEL
from ablauf import ablauf, AblaufFehler
from spielstand import Fortschritt, aufgaben_ids, basis_xp as berechne_basis_xp, xp_fuer_loesung, xp_fuer_quiz

ANTWORT_DATEI = BASIS / "antwort.sql"
SANDBOX_DATEI = BASIS / "sandbox.db"

BEFEHLE_HILFE = f"""{farbe('Befehle während einer Aufgabe:', F.FETT)}
  {farbe('.h', F.CYAN)}          nächster Hinweis (kostet etwas XP)
  {farbe('.e', F.CYAN)}          erwartetes Ergebnis anzeigen
  {farbe('.l', F.CYAN)}          Musterlösung anzeigen (gibt kaum noch XP)
  {farbe('.t', F.CYAN)}          alle Tabellen anzeigen
  {farbe('.s NAME', F.CYAN)}     Struktur + erste Zeilen einer Tabelle
  {farbe('.d', F.CYAN)}          SQL aus der Datei antwort.sql abgeben (für lange Abfragen im Editor)
  {farbe('.p SQL', F.CYAN)}      SQL nur ausprobieren (zählt nicht als Antwort)
  {farbe('.a SQL', F.CYAN)}      Ablauf Schritt für Schritt: was FROM, WHERE, GROUP BY … mit den Zeilen machen
                (.a ohne SQL = deine letzte Eingabe)
  {farbe('.theorie', F.CYAN)}    Theorie der Lektion nochmal lesen
  {farbe('.w', F.CYAN)}          Aufgabe überspringen
  {farbe('.m', F.CYAN)}          zurück ins Menü
SQL über mehrere Zeilen: mit {farbe(';', F.CYAN)} beenden (oder eine leere Zeile drücken)."""


# ---------------------------------------------------------------------------
# Hilfsfunktionen für die Ausgabe
# ---------------------------------------------------------------------------
def cls():
    os.system("cls" if os.name == "nt" else "clear")


def eingabe(prompt=""):
    try:
        return input(prompt)
    except EOFError:
        raise KeyboardInterrupt


def weiter(text="[Enter] weiter"):
    eingabe(farbe(text, F.DIM))


def inline(text):
    return re.sub(r"`([^`]+)`", lambda m: farbe(m.group(1), F.CYAN), text)


def zeige_markup(text):
    """Theorie-Text ausgeben. Seiten werden mit --- getrennt."""
    seiten = re.split(r"^\s*---\s*$", textwrap.dedent(text).strip("\n"), flags=re.M)
    for i, seite in enumerate(seiten, 1):
        print()
        for zeile in seite.strip("\n").split("\n"):
            if zeile.startswith("# "):
                print(farbe("▶ " + zeile[2:], F.FETT, F.GELB))
            elif zeile.startswith("    "):
                print(farbe("  │ ", F.DIM) + farbe(zeile[4:], F.CYAN))
            elif zeile.startswith("! "):
                print(farbe("  MySQL ▸ ", F.LILA, F.FETT) + inline(zeile[2:]))
            elif zeile.startswith("* "):
                print("  • " + inline(zeile[2:]))
            elif zeile.startswith("? "):
                print(farbe("  💡 ", F.GELB) + inline(zeile[2:]))
            else:
                print(inline(zeile))
        if i < len(seiten):
            try:
                weiter(f"\n[Enter] weiter  (Seite {i}/{len(seiten)})")
            except KeyboardInterrupt:
                return


def lies_sql(prompt):
    """Liest SQL (mehrzeilig bis ';' oder Leerzeile) oder einen Punkt-Befehl."""
    zeilen = []
    while True:
        z = eingabe(prompt if not zeilen else farbe("   ...> ", F.DIM))
        if not zeilen:
            if not z.strip():
                continue
            if z.strip().startswith("."):
                return z.strip()
        if not z.strip():
            break
        zeilen.append(z)
        if z.rstrip().endswith(";"):
            break
    return "\n".join(zeilen)


def balken(anteil, breite=20):
    voll = round(anteil * breite)
    return farbe("█" * voll, F.GRUEN) + farbe("░" * (breite - voll), F.DIM)


# ---------------------------------------------------------------------------
# Eine Aufgabe spielen
# ---------------------------------------------------------------------------
def spiele_aufgabe(aufgabe, aid, kopf, fp, theorie=None, ist_boss=False):
    """Rückgabe: 'weiter', 'menu'"""
    typ = aufgabe.get("typ", "abfrage")
    basis_xp = berechne_basis_xp(aufgabe, ist_boss)
    print()
    print(farbe("═" * 72, F.BLAU))
    print(farbe(kopf, F.FETT, F.BLAU) + farbe(f"   (+{basis_xp} XP)", F.GELB)
          + (farbe("  ✔ schon gelöst", F.GRUEN) if fp.erledigt(aid) else ""))
    print(farbe("═" * 72, F.BLAU))
    print(inline(textwrap.dedent(aufgabe["aufgabe"]).strip()))

    if typ == "quiz":
        return spiele_quiz(aufgabe, aid, basis_xp, fp)

    print(farbe("\n(.h Hinweis · .e erwartet · .l Lösung · .a Ablauf · .s tabelle · .d antwort.sql · .? alle Befehle)", F.DIM))
    hinweise = aufgabe.get("hinweise", [])
    hinweis_nr = 0
    loesung_gesehen = False
    letzte_eingabe = None
    while True:
        try:
            eing = lies_sql(farbe("\nSQL> ", F.GRUEN, F.FETT))
        except KeyboardInterrupt:
            print()
            return "menu"
        befehl = eing.split(None, 1)[0].lower() if eing.startswith(".") else None
        arg = eing.split(None, 1)[1] if befehl and len(eing.split(None, 1)) > 1 else ""

        if befehl in (".m", ".menu", ".menü", ".q", ".quit", ".exit"):
            return "menu"
        if befehl in (".w", ".weiter", ".skip"):
            return "weiter"
        if befehl in (".?", ".hilfe", ".help"):
            print(BEFEHLE_HILFE)
            continue
        if befehl in (".h", ".hinweis", ".tipp"):
            if hinweis_nr < len(hinweise):
                hinweis_nr += 1
                print(farbe(f"💡 Hinweis {hinweis_nr}/{len(hinweise)}: ", F.GELB) + inline(hinweise[hinweis_nr - 1]))
            else:
                print(farbe("Keine weiteren Hinweise. Mit .e siehst du das erwartete Ergebnis, mit .l die Lösung.", F.DIM))
            continue
        if befehl in (".l", ".loesung", ".lösung"):
            loesung_gesehen = True
            print(farbe("Musterlösung:", F.LILA, F.FETT))
            print(farbe(textwrap.dedent(aufgabe["loesung"]).strip(), F.CYAN))
            print(farbe("Tipp der Woche: Tipp sie trotzdem selbst ab – Tippen bleibt besser hängen als Lesen.", F.DIM))
            continue
        if befehl in (".e", ".erwartet"):
            zeige_erwartet(aufgabe)
            continue
        if befehl in (".t", ".tabellen", ".tables"):
            conn = neue_db(aufgabe.get("setup"))
            print("Tabellen/Views: " + ", ".join(farbe(t, F.CYAN) for t in leere_tabellenliste(conn)))
            continue
        if befehl in (".s", ".schema"):
            if not arg:
                print(farbe("Benutzung: .s spieler", F.DIM))
                continue
            print(schema_text(neue_db(aufgabe.get("setup")), arg.strip(" ;")))
            continue
        if befehl in (".theorie", ".th"):
            if theorie:
                zeige_markup(theorie)
            continue
        if befehl in (".p", ".probe"):
            if arg:
                print(ergebnis_text(ausfuehren(neue_db(aufgabe.get("setup")), arg)))
            continue
        if befehl in (".a", ".ablauf"):
            if arg or letzte_eingabe:
                zeige_ablauf(neue_db(aufgabe.get("setup")), arg or letzte_eingabe)
            else:
                print(farbe("Benutzung: .a SELECT ... ;", F.DIM))
            continue
        if befehl in (".d", ".datei"):
            eing = lies_antwortdatei()
            if eing is None:
                continue
            print(farbe("Aus antwort.sql:", F.DIM))
            print(farbe(eing, F.CYAN))
        elif befehl:
            print(farbe(f"Unbekannter Befehl {befehl}. .? zeigt alle Befehle.", F.ROT))
            continue

        letzte_eingabe = eing
        ok, meldung, ausgabe = pruefe_aufgabe(aufgabe, eing)
        if ausgabe:
            print(ausgabe)
        if ok:
            xp = xp_fuer_loesung(basis_xp, hinweis_nr, loesung_gesehen)
            vorher = fp.rang
            fp.setze(aid, xp)
            print(farbe(f"\n✔ RICHTIG!  +{xp} XP", F.GRUEN, F.FETT)
                  + farbe(f"   (Gesamt: {fp.xp} XP · Rang: {fp.rang})", F.DIM))
            if fp.rang != vorher:
                print(farbe(f"⚔  Aufstieg! Du bist jetzt: {fp.rang}", F.GELB, F.FETT))
            if aufgabe.get("erklaerung"):
                print(farbe("ℹ  ", F.BLAU) + inline(textwrap.dedent(aufgabe["erklaerung"]).strip()))
            try:
                weiter()
            except KeyboardInterrupt:
                return "menu"
            return "weiter"
        print(farbe("✘ Noch nicht richtig. ", F.ROT, F.FETT) + (meldung or ""))
        if hinweis_nr < len(hinweise):
            print(farbe("  (Tipp: .h für einen Hinweis, .e für das erwartete Ergebnis)", F.DIM))


def zeige_ablauf(conn, sql):
    try:
        schritte = ablauf(conn, sql)
    except AblaufFehler as e:
        print(farbe(f"Ablauf nicht möglich: {e}", F.ROT))
        return
    zeichen = {"raus": "✘ raus", "null": "∅ NULL", "drin": "✔ bleibt", "g0": "▌", "g1": "▐"}
    for n, s in enumerate(schritte, 1):
        print(farbe(f"\n── Schritt {n}/{len(schritte)}: {s['klausel']} – {s['titel']} ", F.GELB, F.FETT) + farbe("─" * 20, F.GELB))
        if s["code"]:
            print(farbe("   " + s["code"], F.CYAN))
        print(textwrap.fill(s["text"], 100))
        if s["spalten"]:
            if any(s["marken"]):
                print(tabelle_text(["→"] + s["spalten"], [[zeichen.get(m, "")] + z for m, z in zip(s["marken"], s["zeilen"])]))
            else:
                print(tabelle_text(s["spalten"], s["zeilen"]))
        if n < len(schritte):
            try:
                if eingabe(farbe("[Enter] nächster Schritt · q = abbrechen ", F.DIM)).strip().lower() == "q":
                    return
            except KeyboardInterrupt:
                return


def spiele_quiz(aufgabe, aid, basis_xp, fp):
    optionen = aufgabe["optionen"]
    for i, o in enumerate(optionen, 1):
        print(f"  {farbe(str(i), F.CYAN, F.FETT)}) {inline(o)}")
    versuche = 0
    while True:
        try:
            antw = eingabe(farbe("\nDeine Antwort (Nummer, .m = Menü): ", F.GRUEN, F.FETT)).strip()
        except KeyboardInterrupt:
            return "menu"
        if antw in (".m", ".menu"):
            return "menu"
        if antw in (".w",):
            return "weiter"
        if not antw.isdigit() or not 1 <= int(antw) <= len(optionen):
            print(farbe(f"Bitte eine Zahl von 1 bis {len(optionen)} eingeben.", F.DIM))
            continue
        versuche += 1
        if int(antw) == aufgabe["richtig"]:
            xp = xp_fuer_quiz(basis_xp, versuche)
            fp.setze(aid, xp)
            print(farbe(f"✔ RICHTIG!  +{xp} XP", F.GRUEN, F.FETT) + farbe(f"   (Gesamt: {fp.xp} XP · Rang: {fp.rang})", F.DIM))
        else:
            print(farbe("✘ Leider falsch.", F.ROT, F.FETT) + (" Versuch es nochmal." if versuche < 2 else
                  f" Richtig wäre {aufgabe['richtig']}) {optionen[aufgabe['richtig'] - 1]}"))
            if versuche < 2:
                continue
        if aufgabe.get("erklaerung"):
            print(farbe("ℹ  ", F.BLAU) + inline(textwrap.dedent(aufgabe["erklaerung"]).strip()))
        try:
            weiter()
        except KeyboardInterrupt:
            return "menu"
        return "weiter"


def zeige_erwartet(aufgabe):
    teile = erwartet(aufgabe)
    if not teile:
        print(farbe("Hier wird geprüft, ob deine Tabelle sich richtig verhält (Tests mit INSERTs). "
                    "Lies die Aufgabe genau – jede geforderte Regel wird getestet.", F.DIM))
        return
    if aufgabe.get("typ", "abfrage") != "abfrage":
        print(farbe("So soll die Datenbank danach aussehen:", F.LILA, F.FETT))
    for titel, erg in teile:
        print(farbe(titel, F.LILA if titel.startswith("Erwartet") else F.DIM, F.FETT))
        print(tabelle_text(erg.spalten, erg.zeilen) if erg.hat_tabelle else farbe(erg.fehler or "", F.ROT))


def lies_antwortdatei():
    if not ANTWORT_DATEI.exists() or not ANTWORT_DATEI.read_text(encoding="utf-8").strip():
        lege_antwortdatei_an()
        print(farbe(f"Die Datei {ANTWORT_DATEI} ist leer. Schreib dein SQL hinein, speichere und tippe .d", F.GELB))
        return None
    text = ANTWORT_DATEI.read_text(encoding="utf-8")
    ohne = "\n".join(z for z in text.splitlines() if not z.strip().startswith("--")).strip()
    if not ohne:
        print(farbe(f"In {ANTWORT_DATEI.name} steht nur ein Kommentar. Schreib dein SQL darunter und speichere.", F.GELB))
        return None
    return text


def lege_antwortdatei_an():
    if not ANTWORT_DATEI.exists():
        ANTWORT_DATEI.write_text("-- Schreib hier dein SQL, speichere die Datei und tippe im Spiel: .d\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Menüs
# ---------------------------------------------------------------------------
def kapitel_menue(k, fp):
    while True:
        cls()
        ids = aufgaben_ids(k)
        fertig = sum(fp.erledigt(i) for i in ids)
        print(farbe(f"Kapitel {k['nr']}: {k['titel']}", F.FETT, F.GELB) + f"   {balken(fertig / len(ids))} {fertig}/{len(ids)}")
        print()
        for li, lek in enumerate(k["lektionen"], 1):
            lids = [f"{k['nr']}.{li}.{ai}" for ai in range(1, len(lek["aufgaben"]) + 1)]
            n = sum(fp.erledigt(i) for i in lids)
            haken = farbe("✔", F.GRUEN) if n == len(lids) else (farbe("◐", F.GELB) if n else " ")
            print(f"  {haken} {farbe(str(li), F.CYAN, F.FETT)}) {lek['titel']}  {farbe(f'{n}/{len(lids)}', F.DIM)}")
        if k.get("boss"):
            bid = f"{k['nr']}.B"
            haken = farbe("✔", F.GRUEN) if fp.erledigt(bid) else " "
            print(f"  {haken} {farbe('B', F.ROT, F.FETT)}) {farbe('BOSSKAMPF: ' + k['boss']['titel'], F.ROT)}")
        print(f"\n    {farbe('Z', F.CYAN, F.FETT)}) Zurück")
        try:
            wahl = eingabe(farbe("\nWahl: ", F.GRUEN, F.FETT)).strip().lower()
        except KeyboardInterrupt:
            return
        if wahl in ("z", "", "q", "m"):
            return
        if wahl == "b" and k.get("boss"):
            boss = k["boss"]
            cls()
            print(farbe(f"☠  BOSSKAMPF: {boss['titel']}", F.ROT, F.FETT))
            if boss.get("story"):
                zeige_markup(boss["story"])
            spiele_aufgabe(boss, f"{k['nr']}.B", f"BOSS · Kapitel {k['nr']}", fp, ist_boss=True)
        elif wahl.isdigit() and 1 <= int(wahl) <= len(k["lektionen"]):
            spiele_lektion(k, int(wahl), fp)


def spiele_lektion(k, li, fp):
    lek = k["lektionen"][li - 1]
    ids = [f"{k['nr']}.{li}.{ai}" for ai in range(1, len(lek["aufgaben"]) + 1)]
    cls()
    print(farbe(f"Lektion {k['nr']}.{li}: {lek['titel']}", F.FETT, F.GELB))
    zeige_theorie = True
    if any(fp.erledigt(i) for i in ids):
        try:
            zeige_theorie = eingabe("Theorie nochmal anzeigen? (j/N) ").strip().lower() == "j"
        except KeyboardInterrupt:
            return
    if zeige_theorie:
        zeige_markup(lek["theorie"])
        try:
            weiter("\n[Enter] zu den Aufgaben")
        except KeyboardInterrupt:
            return
    start = next((i for i, aid in enumerate(ids) if not fp.erledigt(aid)), 0)
    for ai in range(start, len(ids)):
        kopf = f"Aufgabe {ai + 1}/{len(ids)} · Lektion {k['nr']}.{li} {lek['titel']}"
        if spiele_aufgabe(lek["aufgaben"][ai], ids[ai], kopf, fp, theorie=lek["theorie"]) == "menu":
            return
    if all(fp.erledigt(i) for i in ids):
        print(farbe(f"\n🏆 Lektion {k['nr']}.{li} abgeschlossen!", F.GELB, F.FETT))
        try:
            weiter()
        except KeyboardInterrupt:
            pass


def sandbox():
    cls()
    if not SANDBOX_DATEI.exists():
        neue_db(pfad=str(SANDBOX_DATEI)).close()
    conn = neue_db(pfad=str(SANDBOX_DATEI), mit_welt=False)
    print(farbe("SANDBOX – freie SQL-Konsole", F.FETT, F.GELB))
    print("Alles, was du hier machst, wird in sandbox.db gespeichert (bleibt nach dem Beenden erhalten).")
    print(farbe(".t Tabellen · .s NAME Struktur · .a SQL Ablauf · .d antwort.sql ausführen · .reset Welt neu laden · .m Menü", F.DIM))
    while True:
        try:
            eing = lies_sql(farbe("\nsandbox> ", F.LILA, F.FETT))
        except KeyboardInterrupt:
            break
        befehl = eing.split(None, 1)[0].lower() if eing.startswith(".") else None
        if befehl in (".m", ".q", ".menu", ".exit"):
            break
        if befehl in (".t", ".tabellen"):
            print("Tabellen/Views: " + ", ".join(farbe(t, F.CYAN) for t in leere_tabellenliste(conn)))
            continue
        if befehl in (".s", ".schema"):
            teile = eing.split(None, 1)
            if len(teile) > 1:
                print(schema_text(conn, teile[1].strip(" ;")))
            continue
        if befehl in (".a", ".ablauf"):
            teile = eing.split(None, 1)
            if len(teile) > 1:
                kopie = neue_db(mit_welt=False)
                conn.backup(kopie)   # Ablauf soll die Sandbox nicht verändern
                zeige_ablauf(kopie, teile[1])
            continue
        if befehl == ".reset":
            conn.close()
            SANDBOX_DATEI.unlink(missing_ok=True)
            neue_db(pfad=str(SANDBOX_DATEI)).close()
            conn = neue_db(pfad=str(SANDBOX_DATEI), mit_welt=False)
            print(farbe("Spielwelt frisch geladen.", F.GRUEN))
            continue
        if befehl in (".d", ".datei"):
            eing = lies_antwortdatei()
            if eing is None:
                continue
        elif befehl:
            print(farbe("Unbekannter Befehl.", F.ROT))
            continue
        print(ergebnis_text(ausfuehren(conn, eing)))
    conn.close()


def hauptmenue(fp):
    while True:
        cls()
        print(farbe(r"""
   ____   ___  _          ___                  _
  / ___| / _ \| |        / _ \ _   _  ___  ___| |_
  \___ \| | | | |  _____| | | | | | |/ _ \/ __| __|
   ___) | |_| | |__|_____| |_| | |_| |  __/\__ \ |_
  |____/ \__\_\_____|     \__\_\\__,_|\___||___/\__|
""", F.GELB, F.FETT))
        nr = fp.naechster_rang()
        print(f"  Rang: {farbe(fp.rang, F.GELB, F.FETT)}   XP: {farbe(fp.xp, F.GRUEN, F.FETT)}"
              + (farbe(f"   (nächster Rang '{nr[1]}' ab {nr[0]} XP)", F.DIM) if nr else ""))
        print()
        for k in ALLE_KAPITEL:
            ids = aufgaben_ids(k)
            n = sum(fp.erledigt(i) for i in ids)
            haken = farbe("✔", F.GRUEN) if n == len(ids) else " "
            print(f"  {haken} {farbe(str(k['nr']).rjust(2), F.CYAN, F.FETT)}) {k['titel'].ljust(34)} {balken(n / len(ids), 15)} {farbe(f'{n}/{len(ids)}', F.DIM)}")
        print()
        print(f"     {farbe('S', F.LILA, F.FETT)}) Sandbox (freie SQL-Konsole)")
        print(f"     {farbe('H', F.CYAN, F.FETT)}) Hilfe / Befehle")
        print(f"     {farbe('R', F.CYAN, F.FETT)}) Fortschritt zurücksetzen")
        print(f"     {farbe('Q', F.CYAN, F.FETT)}) Beenden")
        try:
            wahl = eingabe(farbe("\nWahl: ", F.GRUEN, F.FETT)).strip().lower()
        except KeyboardInterrupt:
            return
        if wahl == "q":
            return
        if wahl == "s":
            sandbox()
        elif wahl == "h":
            cls()
            print(BEFEHLE_HILFE)
            print("\nDateien:\n  antwort.sql   – hier kannst du längere Abfragen im Editor schreiben (.d gibt sie ab)"
                  "\n  sandbox.db    – deine Spielwiese aus der Sandbox"
                  "\n  LEHRPLAN.md   – was in welchem Kapitel drankommt"
                  "\n  SPICKZETTEL.md – alle Befehle auf einen Blick")
            weiter()
        elif wahl == "r":
            if eingabe("Wirklich ALLES zurücksetzen? (ja/nein) ").strip().lower() == "ja":
                fp.zuruecksetzen()
        elif wahl.isdigit():
            k = next((k for k in ALLE_KAPITEL if k["nr"] == int(wahl)), None)
            if k:
                kapitel_menue(k, fp)


def main():
    os.system("")  # ANSI-Farben unter Windows aktivieren
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    lege_antwortdatei_an()
    fp = Fortschritt()
    try:
        hauptmenue(fp)
    except KeyboardInterrupt:
        pass
    print(farbe(f"\nBis bald, {fp.rang}! Dein Fortschritt ist gespeichert ({fp.xp} XP).", F.GELB))


if __name__ == "__main__":
    main()
