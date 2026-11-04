"""
Spielstand und XP-Regeln – gemeinsam für Terminal (spielen.py) und Oberfläche (web.py).
"""
import json

from engine import BASIS
from kapitel import ALLE_KAPITEL

FORTSCHRITT_DATEI = BASIS / "fortschritt.json"

XP = {"abfrage": 10, "aendern": 10, "quiz": 5, "boss": 30}
RAENGE = [(0, "Bauer"), (60, "Lehrling"), (180, "Knappe"), (350, "Abenteurer"), (550, "Ritter der Tabellen"),
          (800, "Magier der Abfragen"), (1100, "Join-Meister"), (1400, "Index-Großmeister"), (1700, "Datenbank-Drache")]


class Fortschritt:
    def __init__(self):
        self.daten = {"erledigt": {}}
        if FORTSCHRITT_DATEI.exists():
            try:
                self.daten = json.loads(FORTSCHRITT_DATEI.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        self.daten.setdefault("erledigt", {})

    def speichern(self):
        FORTSCHRITT_DATEI.write_text(json.dumps(self.daten, indent=2, ensure_ascii=False), encoding="utf-8")

    def erledigt(self, aid):
        return aid in self.daten["erledigt"]

    def setze(self, aid, xp):
        alt = self.daten["erledigt"].get(aid, -1)
        if xp > alt:
            self.daten["erledigt"][aid] = xp
            self.speichern()

    def zuruecksetzen(self):
        self.daten = {"erledigt": {}}
        self.speichern()

    @property
    def xp(self):
        return sum(self.daten["erledigt"].values())

    @property
    def rang(self):
        return [name for grenze, name in RAENGE if self.xp >= grenze][-1]

    def naechster_rang(self):
        for grenze, name in RAENGE:
            if self.xp < grenze:
                return grenze, name
        return None


def basis_xp(aufgabe, ist_boss=False):
    return XP["boss"] if ist_boss else XP[aufgabe.get("typ", "abfrage")]


def xp_fuer_loesung(basis, hinweise, loesung_gesehen):
    """XP für eine gelöste SQL-Aufgabe: Hinweise kosten je 3, die Musterlösung fast alles."""
    return 2 if loesung_gesehen else max(3, basis - 3 * hinweise)


def xp_fuer_quiz(basis, versuch):
    return basis if versuch == 1 else 1


def aufgaben_ids(k):
    ids = []
    for li, lek in enumerate(k["lektionen"], 1):
        ids += [f"{k['nr']}.{li}.{ai}" for ai in range(1, len(lek["aufgaben"]) + 1)]
    if k.get("boss"):
        ids.append(f"{k['nr']}.B")
    return ids


def alle_ids():
    return [aid for k in ALLE_KAPITEL for aid in aufgaben_ids(k)]


def finde_aufgabe(aid):
    """Rückgabe: (kapitel, lektion_oder_None, aufgabe, ist_boss) – oder None."""
    teile = aid.split(".")
    k = next((k for k in ALLE_KAPITEL if str(k["nr"]) == teile[0]), None)
    if k is None:
        return None
    if len(teile) == 2 and teile[1] == "B" and k.get("boss"):
        return k, None, k["boss"], True
    try:
        lek = k["lektionen"][int(teile[1]) - 1]
        return k, lek, lek["aufgaben"][int(teile[2]) - 1], False
    except (IndexError, ValueError):
        return None
