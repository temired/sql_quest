"""
SQL-Quest mit Oberfläche im Browser: Aufgabe links, SQL-Editor + Ergebnis rechts.
Start:  python web.py        (öffnet automatisch den Browser)

Läuft komplett lokal (nur Python-Standardbibliothek, kein Internet nötig) und benutzt
denselben Spielstand (fortschritt.json) wie die Terminal-Version spielen.py.
"""
import json
import os
import sys
import textwrap
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from ablauf import ablauf, AblaufFehler
from engine import BASIS, neue_db, ausfuehren, pruefe_aufgabe_roh, erwartet, leere_tabellenliste
from kapitel import ALLE_KAPITEL
from spielstand import (Fortschritt, aufgaben_ids, alle_ids, finde_aufgabe, basis_xp,
                        xp_fuer_loesung, xp_fuer_quiz)

WEB_ORDNER = BASIS / "web"
SANDBOX_DATEI = BASIS / "sandbox.db"
MAX_ZEILEN = 200
STARTPORT = 8765

MIME = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8", ".svg": "image/svg+xml"}


def dedent(text):
    return textwrap.dedent(text or "").strip("\n")


def ergebnis_json(erg):
    zeilen = erg.zeilen or []
    return {
        "spalten": erg.spalten,
        "zeilen": [list(z) for z in zeilen[:MAX_ZEILEN]],
        "anzahl": len(zeilen),
        "meldungen": erg.meldungen,
        "fehler": erg.fehler,
        "roh_fehler": erg.roh_fehler if erg.roh_fehler != erg.fehler else None,
    }


def db_fuer(aid):
    """Frische DB für eine Aufgabe – oder die gespeicherte Sandbox."""
    if aid == "sandbox":
        if not SANDBOX_DATEI.exists():
            neue_db(pfad=str(SANDBOX_DATEI)).close()
        return neue_db(pfad=str(SANDBOX_DATEI), mit_welt=False)
    gefunden = finde_aufgabe(aid)
    return neue_db(gefunden[2].get("setup") if gefunden else None)


def schema(conn):
    tabellen = []
    for name in leere_tabellenliste(conn):
        spalten = [{"name": n, "typ": t, "pk": pk > 0, "notnull": bool(nn)}
                   for n, t, nn, pk in conn.execute(
                       f"SELECT name, type, \"notnull\", pk FROM pragma_table_info('{name}') ORDER BY cid")]
        fks = {von: f"{tab}({nach})" for von, tab, nach in conn.execute(
            f"SELECT \"from\", \"table\", \"to\" FROM pragma_foreign_key_list('{name}')")}
        for s in spalten:
            s["fk"] = fks.get(s["name"])
        art = conn.execute("SELECT type FROM sqlite_master WHERE name = ?", (name,)).fetchone()[0]
        tabellen.append({"name": name, "art": art, "spalten": spalten})
    return tabellen


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
def api_uebersicht(_):
    fp = Fortschritt()
    kapitel = []
    for k in ALLE_KAPITEL:
        ids = aufgaben_ids(k)
        lektionen = []
        for li, lek in enumerate(k["lektionen"], 1):
            lektionen.append({"titel": lek["titel"], "aufgaben": [
                {"id": f"{k['nr']}.{li}.{ai}", "typ": a.get("typ", "abfrage"), "erledigt": fp.erledigt(f"{k['nr']}.{li}.{ai}")}
                for ai, a in enumerate(lek["aufgaben"], 1)]})
        boss = None
        if k.get("boss"):
            boss = {"id": f"{k['nr']}.B", "titel": k["boss"]["titel"], "erledigt": fp.erledigt(f"{k['nr']}.B")}
        kapitel.append({"nr": k["nr"], "titel": k["titel"], "gesamt": len(ids),
                        "fertig": sum(fp.erledigt(i) for i in ids), "lektionen": lektionen, "boss": boss})
    naechster = fp.naechster_rang()
    return {"xp": fp.xp, "rang": fp.rang, "naechster": {"xp": naechster[0], "rang": naechster[1]} if naechster else None,
            "kapitel": kapitel}


def api_aufgabe(d):
    aid = d["id"]
    gefunden = finde_aufgabe(aid)
    if not gefunden:
        raise KeyError(f"Aufgabe {aid} gibt es nicht.")
    k, lek, a, ist_boss = gefunden
    fp = Fortschritt()
    ids = alle_ids()
    pos = ids.index(aid)
    if ist_boss:
        nr_in_lektion, anzahl = 1, 1
    else:
        nr_in_lektion, anzahl = int(aid.split(".")[2]), len(lek["aufgaben"])
    return {
        "id": aid, "typ": a.get("typ", "abfrage"), "ist_boss": ist_boss,
        "kapitel_nr": k["nr"], "kapitel_titel": k["titel"],
        "lektion_titel": a["titel"] if ist_boss else lek["titel"],
        "nr": nr_in_lektion, "anzahl": anzahl,
        "text": dedent(a["aufgabe"]),
        "theorie": dedent(a.get("story") if ist_boss else lek["theorie"]),
        "hinweise": len(a.get("hinweise", [])),
        "optionen": a.get("optionen"),
        "xp_basis": basis_xp(a, ist_boss),
        "erledigt": fp.erledigt(aid), "xp_erhalten": fp.daten["erledigt"].get(aid),
        "vorher": ids[pos - 1] if pos > 0 else None,
        "nachher": ids[pos + 1] if pos + 1 < len(ids) else None,
    }


def _aufgabe(d):
    gefunden = finde_aufgabe(d["id"])
    if not gefunden:
        raise KeyError(f"Aufgabe {d['id']} gibt es nicht.")
    return gefunden


def api_hinweis(d):
    hinweise = _aufgabe(d)[2].get("hinweise", [])
    nr = int(d.get("nr", 1))
    return {"text": hinweise[nr - 1] if 1 <= nr <= len(hinweise) else None}


def api_loesung(d):
    return {"loesung": dedent(_aufgabe(d)[2]["loesung"])}


def api_erwartet(d):
    a = _aufgabe(d)[2]
    return {"teile": [{"titel": t, "ergebnis": ergebnis_json(e)} for t, e in erwartet(a)],
            "aendern": a.get("typ", "abfrage") != "abfrage"}


def api_ausfuehren(d):
    conn = db_fuer(d["id"])
    try:
        return {"ergebnis": ergebnis_json(ausfuehren(conn, d.get("sql", "")))}
    finally:
        conn.close()


def api_abgeben(d):
    k, lek, a, ist_boss = _aufgabe(d)
    ok, meldung, erg = pruefe_aufgabe_roh(a, d.get("sql", ""))
    antwort = {"ok": ok, "meldung": meldung, "ergebnis": ergebnis_json(erg)}
    if ok:
        fp = Fortschritt()
        vorher = fp.rang
        xp = xp_fuer_loesung(basis_xp(a, ist_boss), int(d.get("hinweise", 0)), bool(d.get("loesung_gesehen")))
        fp.setze(d["id"], xp)
        antwort.update(xp=xp, gesamt_xp=fp.xp, rang=fp.rang, aufstieg=fp.rang != vorher,
                       erklaerung=dedent(a.get("erklaerung")))
    return antwort


def api_quiz(d):
    k, lek, a, ist_boss = _aufgabe(d)
    versuch = int(d.get("versuch", 1))
    ok = int(d["antwort"]) == a["richtig"]
    antwort = {"ok": ok}
    if ok:
        fp = Fortschritt()
        vorher = fp.rang
        xp = xp_fuer_quiz(basis_xp(a, ist_boss), versuch)
        fp.setze(d["id"], xp)
        antwort.update(xp=xp, gesamt_xp=fp.xp, rang=fp.rang, aufstieg=fp.rang != vorher)
    if ok or versuch >= 2:
        antwort.update(richtig=a["richtig"], erklaerung=dedent(a.get("erklaerung")))
    return antwort


def api_schema(d):
    conn = db_fuer(d["id"])
    try:
        return {"tabellen": schema(conn)}
    finally:
        conn.close()


def api_vorschau(d):
    conn = db_fuer(d["id"])
    try:
        name = d["tabelle"]
        if name not in leere_tabellenliste(conn):
            raise KeyError(f"Tabelle {name} gibt es nicht.")
        return {"ergebnis": ergebnis_json(ausfuehren(conn, f'SELECT * FROM "{name}" LIMIT 10;'))}
    finally:
        conn.close()


def api_sandbox_reset(_):
    SANDBOX_DATEI.unlink(missing_ok=True)
    neue_db(pfad=str(SANDBOX_DATEI)).close()
    return {"ok": True}


def api_ablauf(d):
    quelle = db_fuer(d["id"])
    if d["id"] == "sandbox":
        # in einer Kopie arbeiten, damit die Ablauf-Ansicht die Sandbox nicht verändert
        conn = neue_db(mit_welt=False)
        quelle.backup(conn)
        quelle.close()
    else:
        conn = quelle
    try:
        return {"schritte": ablauf(conn, d.get("sql", ""))}
    except AblaufFehler as e:
        return {"fehler": str(e)}
    finally:
        conn.close()


def api_reset(_):
    Fortschritt().zuruecksetzen()
    return {"ok": True}


API = {"uebersicht": api_uebersicht, "aufgabe": api_aufgabe, "hinweis": api_hinweis, "loesung": api_loesung,
       "erwartet": api_erwartet, "ausfuehren": api_ausfuehren, "abgeben": api_abgeben, "quiz": api_quiz,
       "schema": api_schema, "vorschau": api_vorschau, "sandbox_reset": api_sandbox_reset, "reset": api_reset,
       "ablauf": api_ablauf}


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # Konsole ruhig halten

    def _senden(self, status, inhalt, typ):
        self.send_response(status)
        self.send_header("Content-Type", typ)
        self.send_header("Content-Length", str(len(inhalt)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(inhalt)

    def _json(self, status, daten):
        self._senden(status, json.dumps(daten, ensure_ascii=False, default=str).encode("utf-8"),
                     "application/json; charset=utf-8")

    def do_GET(self):
        pfad = urlparse(self.path).path
        if pfad == "/":
            pfad = "/index.html"
        datei = (WEB_ORDNER / pfad.lstrip("/")).resolve()
        if WEB_ORDNER.resolve() not in datei.parents or not datei.is_file():
            self._senden(404, b"Nicht gefunden", "text/plain; charset=utf-8")
            return
        self._senden(200, datei.read_bytes(), MIME.get(datei.suffix, "application/octet-stream"))

    def do_POST(self):
        name = urlparse(self.path).path.removeprefix("/api/")
        funktion = API.get(name)
        if funktion is None:
            self._json(404, {"fehler": f"Unbekannte API: {name}"})
            return
        try:
            laenge = int(self.headers.get("Content-Length", 0))
            daten = json.loads(self.rfile.read(laenge) or b"{}")
            self._json(200, funktion(daten))
        except Exception as e:  # Fehler an die Oberfläche melden statt den Server abstürzen zu lassen
            self._json(400, {"fehler": str(e)})


class Server(ThreadingHTTPServer):
    # Unter Windows erlaubt SO_REUSEADDR, dass sich zwei Server denselben Port teilen –
    # dann würde ein zweites "python web.py" still einen alten Server überlagern.
    allow_reuse_address = os.name != "nt"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except AttributeError:
        pass
    server = None
    startport = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else STARTPORT
    for port in range(startport, startport + 20):
        try:
            server = Server(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    if server is None:
        print("Kein freier Port gefunden.")
        return
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"SQL-Quest läuft auf {url}")
    print("Der Browser öffnet sich gleich. Fenster offen lassen – beenden mit Strg+C.")
    if "--kein-browser" not in sys.argv:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBeendet. Dein Fortschritt ist gespeichert.")


if __name__ == "__main__":
    main()
