"""
Engine von SQL-Quest: Datenbank anlegen, SQL ausführen (mit MySQL-Kompatibilität),
Ergebnisse vergleichen und hübsch als Tabelle ausgeben.
"""
import re
import sqlite3
import time
from datetime import date, datetime
from pathlib import Path

BASIS = Path(__file__).resolve().parent
WELT_SQL = (BASIS / "daten" / "welt.sql").read_text(encoding="utf-8")

MAX_ZEILEN_ANZEIGE = 25
ZEITLIMIT_SEKUNDEN = 3


# ---------------------------------------------------------------------------
# Farben (ANSI). Windows 10/11 Terminal kann das, os.system("") schaltet es frei.
# ---------------------------------------------------------------------------
class F:
    RESET = "\033[0m"
    FETT = "\033[1m"
    DIM = "\033[2m"
    ROT = "\033[91m"
    GRUEN = "\033[92m"
    GELB = "\033[93m"
    BLAU = "\033[94m"
    LILA = "\033[95m"
    CYAN = "\033[96m"


def farbe(text, *codes):
    return "".join(codes) + str(text) + F.RESET


# ---------------------------------------------------------------------------
# MySQL-Funktionen, die SQLite nicht kennt
# ---------------------------------------------------------------------------
def _datum(s):
    if s is None:
        return None
    s = str(s)
    try:
        return datetime.fromisoformat(s[:19]).date() if len(s) > 10 else date.fromisoformat(s[:10])
    except ValueError:
        return None


def _teil(feld):
    def f(s):
        d = _datum(s)
        return None if d is None else getattr(d, feld)
    return f


def _datediff(a, b):
    da, db = _datum(a), _datum(b)
    return None if da is None or db is None else (da - db).days


def _right(s, n):
    if s is None or n is None:
        return None
    s = str(s)
    return s[-n:] if n > 0 else ""


def _left(s, n):
    return None if s is None or n is None else str(s)[:max(n, 0)]


def _date_format(d, fmt):
    dt = _datum(d)
    if dt is None or fmt is None:
        return None
    teile = {"Y": f"{dt.year:04d}", "y": f"{dt.year % 100:02d}", "m": f"{dt.month:02d}", "c": str(dt.month),
             "d": f"{dt.day:02d}", "e": str(dt.day), "%": "%"}
    return re.sub(r"%(.)", lambda m: teile.get(m.group(1), m.group(0)), fmt)


def _registriere_funktionen(conn):
    conn.create_function("YEAR", 1, _teil("year"), deterministic=True)
    conn.create_function("MONTH", 1, _teil("month"), deterministic=True)
    conn.create_function("DAY", 1, _teil("day"), deterministic=True)
    conn.create_function("DAYOFMONTH", 1, _teil("day"), deterministic=True)
    conn.create_function("DATEDIFF", 2, _datediff, deterministic=True)
    conn.create_function("CURDATE", 0, lambda: date.today().isoformat())
    conn.create_function("CURRENT_DATE", 0, lambda: date.today().isoformat())
    conn.create_function("NOW", 0, lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    conn.create_function("LEFT", 2, _left, deterministic=True)
    conn.create_function("RIGHT", 2, _right, deterministic=True)
    conn.create_function("UCASE", 1, lambda s: None if s is None else str(s).upper(), deterministic=True)
    conn.create_function("LCASE", 1, lambda s: None if s is None else str(s).lower(), deterministic=True)
    conn.create_function("CHAR_LENGTH", 1, lambda s: None if s is None else len(str(s)), deterministic=True)
    conn.create_function("DATE_FORMAT", 2, _date_format, deterministic=True)
    conn.create_function("RAND", 0, lambda: __import__("random").random())


# ---------------------------------------------------------------------------
# Datenbank
# ---------------------------------------------------------------------------
def neue_db(setup=None, pfad=":memory:", mit_welt=True):
    """Frische Datenbank mit der Spielwelt (+ optionalem Setup-SQL)."""
    conn = sqlite3.connect(pfad, autocommit=True)
    _registriere_funktionen(conn)
    conn.execute("PRAGMA foreign_keys = ON")
    if mit_welt:
        conn.executescript(WELT_SQL)
    if setup:
        conn.executescript(setup)
    return conn


def leere_tabellenliste(conn):
    return [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY type, name")]


# ---------------------------------------------------------------------------
# SQL zerlegen und MySQL-Schreibweisen übersetzen
# ---------------------------------------------------------------------------
def zerlege(sql):
    """Teilt einen Text in einzelne SQL-Anweisungen (Strings/Trigger werden beachtet)."""
    teile, puffer = [], ""
    for stueck in sql.split(";"):
        puffer += stueck + ";"
        if sqlite3.complete_statement(puffer):
            if _ohne_kommentare(puffer).strip(" ;\n\t\r"):
                teile.append(puffer.strip())
            puffer = ""
    if _ohne_kommentare(puffer).strip(" ;\n\t\r"):
        teile.append(puffer.strip().rstrip(";") + ";")
    return teile


def _ohne_kommentare(sql):
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    return re.sub(r"--[^\n]*", " ", sql)


def _ersetze_auto_increment(sql):
    # "id INT AUTO_INCREMENT PRIMARY KEY" / "id INT PRIMARY KEY AUTO_INCREMENT" / "id INT NOT NULL AUTO_INCREMENT ..."
    def spalte(m):
        name, rest = m.group(1), m.group(3)
        rest = re.sub(r"\bAUTO_INCREMENT\b|\bPRIMARY\s+KEY\b|\bNOT\s+NULL\b|\bUNSIGNED\b", " ", rest, flags=re.I)
        rest = re.sub(r"\s+", " ", rest).strip()
        return f"{name} INTEGER PRIMARY KEY AUTOINCREMENT" + (f" {rest}" if rest else "")
    sql = re.sub(r"(\w+)\s+(INT|INTEGER|BIGINT|SMALLINT|MEDIUMINT|TINYINT)(?:\(\d+\))?((?:\s+(?:UNSIGNED|NOT\s+NULL|AUTO_INCREMENT|PRIMARY\s+KEY))*\s+AUTO_INCREMENT(?:\s+(?:UNSIGNED|NOT\s+NULL|AUTO_INCREMENT|PRIMARY\s+KEY))*)",
                 lambda m: spalte(m) if re.search(r"PRIMARY\s+KEY", m.group(3), re.I) else m.group(0), sql, flags=re.I)
    # Variante: "id INT AUTO_INCREMENT, ..., PRIMARY KEY (id)"
    m = re.search(r"(\w+)\s+(?:INT|INTEGER|BIGINT)(?:\(\d+\))?(?:\s+UNSIGNED)?(?:\s+NOT\s+NULL)?\s+AUTO_INCREMENT\b", sql, flags=re.I)
    if m:
        spaltenname = m.group(1)
        pk = re.search(r",\s*PRIMARY\s+KEY\s*\(\s*`?" + re.escape(spaltenname) + r"`?\s*\)", sql, flags=re.I)
        if pk:
            sql = sql[:pk.start()] + sql[pk.end():]
            sql = sql[:m.start()] + f"{spaltenname} INTEGER PRIMARY KEY AUTOINCREMENT" + sql[m.end():]
    return re.sub(r"\bAUTO_INCREMENT\b(\s*=\s*\d+)?", "", sql, flags=re.I)


def uebersetze(stmt):
    """Übersetzt eine MySQL-Anweisung nach SQLite.
    Rückgabe: (sql_oder_None, hinweis_oder_None). sql=None heißt: nichts ausführen."""
    s = stmt.strip().rstrip(";").strip()
    kern = _ohne_kommentare(s).strip()
    oben = re.sub(r"\s+", " ", kern).upper()

    if re.match(r"^USE\s+\w+$", oben):
        return None, "USE ignoriert – im Spiel gibt es nur eine Datenbank (rpg_spielwelt)."
    if re.match(r"^(CREATE|DROP)\s+(DATABASE|SCHEMA)\b", oben):
        return None, "CREATE/DROP DATABASE ist in MySQL korrekt – im Spiel gibt es aber nur eine Datenbank."
    if oben in ("SHOW TABLES", "SHOW FULL TABLES"):
        return ("SELECT name AS Tables_in_rpg_spielwelt FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"), None
    m = re.match(r"^(?:DESCRIBE|DESC|SHOW\s+COLUMNS\s+FROM)\s+`?(\w+)`?$", kern, flags=re.I)
    if m:
        return (f"SELECT name AS Field, type AS Type, CASE \"notnull\" WHEN 1 THEN 'NO' ELSE 'YES' END AS \"Null\", "
                f"CASE WHEN pk > 0 THEN 'PRI' ELSE '' END AS \"Key\", dflt_value AS \"Default\" "
                f"FROM pragma_table_info('{m.group(1)}') ORDER BY cid"), None
    m = re.match(r"^SHOW\s+(?:INDEX|INDEXES|KEYS)\s+FROM\s+`?(\w+)`?$", kern, flags=re.I)
    if m:
        return (f"SELECT il.name AS Key_name, ii.name AS Column_name, CASE il.\"unique\" WHEN 1 THEN 0 ELSE 1 END AS Non_unique "
                f"FROM pragma_index_list('{m.group(1)}') il, pragma_index_info(il.name) ii"), None
    m = re.match(r"^SET\s+(?:SESSION\s+|GLOBAL\s+|@@)?FOREIGN_KEY_CHECKS\s*=\s*([01])$", oben)
    if m:
        return f"PRAGMA foreign_keys = {'ON' if m.group(1) == '1' else 'OFF'}", None
    if oben == "START TRANSACTION":
        return "BEGIN", None
    m = re.match(r"^TRUNCATE\s+(?:TABLE\s+)?`?(\w+)`?$", kern, flags=re.I)
    if m:
        return f"DELETE FROM {m.group(1)}", "TRUNCATE wurde als DELETE FROM ausgeführt (SQLite kennt kein TRUNCATE)."
    if re.match(r"^ALTER\s+TABLE\s+\w+\s+(MODIFY|CHANGE)\b", oben):
        return None, ("ALTER TABLE ... MODIFY/CHANGE gibt es nur in MySQL. SQLite kann Spaltentypen nicht ändern. "
                      "Im Spiel: ADD COLUMN, RENAME COLUMN, DROP COLUMN, RENAME TO.")
    if re.match(r"^EXPLAIN\s+(?!QUERY\s+PLAN)", oben):
        s = re.sub(r"^\s*EXPLAIN\s+", "EXPLAIN QUERY PLAN ", s, flags=re.I)
    m = re.match(r"^RENAME\s+TABLE\s+`?(\w+)`?\s+TO\s+`?(\w+)`?$", kern, flags=re.I)
    if m:
        return f"ALTER TABLE {m.group(1)} RENAME TO {m.group(2)}", None
    m = re.match(r"^DROP\s+INDEX\s+`?(\w+)`?\s+ON\s+`?\w+`?$", kern, flags=re.I)
    if m:
        return f"DROP INDEX {m.group(1)}", None
    m = re.match(r"^ALTER\s+TABLE\s+`?(\w+)`?\s+ADD\s+(UNIQUE\s+)?(?:INDEX|KEY)\s+`?(\w+)`?\s*(\(.*\))$", kern, flags=re.I | re.S)
    if m:
        return f"CREATE {m.group(2) or ''}INDEX {m.group(3)} ON {m.group(1)} {m.group(4)}", None
    if re.match(r"^ALTER\s+TABLE\s+\w+\s+ADD\s+(CONSTRAINT|FOREIGN\s+KEY|PRIMARY\s+KEY)", oben):
        return None, ("ALTER TABLE ... ADD CONSTRAINT/FOREIGN KEY/PRIMARY KEY geht in MySQL, aber nicht in SQLite. "
                      "Im Spiel bitte Schlüssel direkt im CREATE TABLE angeben.")

    if re.match(r"^(CREATE|ALTER)\s+TABLE", oben):
        s = _ersetze_auto_increment(s)
        s = re.sub(r"\)\s*(ENGINE|DEFAULT\s+CHARSET|CHARSET|COLLATE)\b.*$", ")", s, flags=re.I | re.S)
        s = re.sub(r"\bUNSIGNED\b", "", s, flags=re.I)
        s = re.sub(r"(\w+)\s+ENUM\s*\(([^)]*)\)", r"\1 TEXT CHECK (\1 IN (\2))", s, flags=re.I)
    # MySQL: GROUP_CONCAT(x ORDER BY y SEPARATOR ', ')  →  SQLite: GROUP_CONCAT(x, ', ' ORDER BY y)
    s = re.sub(r"GROUP_CONCAT\s*\(\s*(DISTINCT\s+)?(.+?)(\s+ORDER\s+BY\s+[^)]+?)?(?:\s+SEPARATOR\s+('[^']*'))?\s*\)",
               lambda m: f"GROUP_CONCAT({m.group(1) or ''}{m.group(2)}, {m.group(4) or chr(39) + ',' + chr(39)}{m.group(3) or ''})"
               if m.group(4) or (m.group(3) and "," not in m.group(2)) else m.group(0), s, flags=re.I)
    return s, None


# ---------------------------------------------------------------------------
# Ausführen
# ---------------------------------------------------------------------------
class Ergebnis:
    def __init__(self):
        self.spalten = None      # Spaltennamen der letzten Abfrage mit Ergebnis
        self.zeilen = None
        self.meldungen = []      # Infos pro Anweisung
        self.fehler = None       # Fehlertext (übersetzt)
        self.roh_fehler = None

    @property
    def hat_tabelle(self):
        return self.spalten is not None


def ausfuehren(conn, sql):
    erg = Ergebnis()
    start = [time.monotonic()]
    conn.set_progress_handler(lambda: 1 if time.monotonic() - start[0] > ZEITLIMIT_SEKUNDEN else 0, 20000)
    try:
        for stmt in zerlege(sql):
            start[0] = time.monotonic()
            uebersetzt, hinweis = uebersetze(stmt)
            if hinweis:
                erg.meldungen.append(hinweis)
            if uebersetzt is None:
                continue
            try:
                cur = conn.execute(uebersetzt)
            except sqlite3.Error as e:
                erg.roh_fehler = str(e)
                erg.fehler = uebersetze_fehler(str(e), stmt)
                return erg
            if cur.description:
                erg.spalten = [d[0] for d in cur.description]
                erg.zeilen = cur.fetchall()
            else:
                art = _ohne_kommentare(stmt).strip().split(None, 1)[0].upper() if stmt.strip() else ""
                if art in ("INSERT", "UPDATE", "DELETE", "REPLACE") and cur.rowcount >= 0:
                    erg.meldungen.append(f"{art}: {cur.rowcount} Zeile(n) betroffen.")
                elif art:
                    erg.meldungen.append(f"{art} ausgeführt.")
    finally:
        conn.set_progress_handler(None, 0)
    return erg


FEHLER_UEBERSETZUNG = [
    (r"no such table: (\S+)", "Tabelle '{0}' gibt es nicht. Tipp: .tabellen zeigt alle Tabellen."),
    (r"no such column: (\S+)", "Spalte '{0}' gibt es nicht. Tipp: .s tabellenname zeigt die Spalten. (Strings brauchen 'einfache' Anführungszeichen!)"),
    (r"no such function: (\S+)", "Die Funktion '{0}' gibt es hier nicht."),
    (r'near "(.*?)": syntax error', "Syntaxfehler in der Nähe von '{0}'. Prüfe Kommas, Klammern, Schlüsselwörter und Reihenfolge."),
    (r"incomplete input", "Die Anweisung ist unvollständig (fehlt eine Klammer oder ein Anführungszeichen?)."),
    (r"UNIQUE constraint failed: (\S+)", "UNIQUE verletzt: Der Wert in {0} existiert schon."),
    (r"NOT NULL constraint failed: (\S+)", "NOT NULL verletzt: {0} darf nicht leer (NULL) sein."),
    (r"CHECK constraint failed: (.+)", "CHECK verletzt: Bedingung '{0}' ist nicht erfüllt."),
    (r"FOREIGN KEY constraint failed", "FOREIGN KEY verletzt: Der Wert verweist auf keinen existierenden Datensatz (oder wird noch referenziert)."),
    (r"ambiguous column name: (\S+)", "Spalte '{0}' ist mehrdeutig – sie gibt es in mehreren Tabellen. Schreib tabelle.{0} bzw. alias.{0}."),
    (r"misuse of aggregate.*?: (\S+)", "Aggregatfunktion {0} falsch benutzt. Aggregate gehören nicht in WHERE – nutze HAVING."),
    (r"misuse of aggregate", "Aggregatfunktion falsch benutzt. Aggregate gehören nicht in WHERE – nutze HAVING."),
    (r"table (\S+) already exists", "Tabelle {0} existiert schon. (Tipp: CREATE TABLE IF NOT EXISTS oder vorher DROP TABLE)"),
    (r"(\S+) has no column named (\S+)", "Tabelle {0} hat keine Spalte '{1}'."),
    (r"table (\S+) has (\d+) columns but (\d+) values were supplied", "Tabelle {0} hat {1} Spalten, du lieferst aber {2} Werte. Gib eine Spaltenliste an!"),
    (r"(\d+) values for (\d+) columns", "Anzahl Werte ({0}) passt nicht zur Anzahl Spalten ({1})."),
    (r"SELECTs to the left and right of (\S+) do not have the same number of result columns",
     "Bei {0} müssen beide SELECTs gleich viele Spalten haben."),
    (r"interrupted", "Abbruch: Die Abfrage lief länger als {} Sekunden (Endlosschleife oder riesiges Kreuzprodukt?).".format(ZEITLIMIT_SEKUNDEN)),
    (r"cannot start a transaction within a transaction", "Es läuft schon eine Transaktion. Erst COMMIT oder ROLLBACK."),
    (r"cannot (commit|rollback) - no transaction is active", "Es ist keine Transaktion aktiv (erst BEGIN / START TRANSACTION)."),
    (r"a GROUP BY clause is required before HAVING", "HAVING braucht ein GROUP BY davor."),
    (r"sub-select returns (\d+) columns - expected 1", "Die Unterabfrage liefert {0} Spalten, erwartet wird genau 1."),
    (r"row value misused", "Klammer-Ausdruck falsch benutzt (z.B. IN (...) mit mehreren Spalten?)."),
]


def uebersetze_fehler(text, stmt=""):
    for muster, deutsch in FEHLER_UEBERSETZUNG:
        m = re.search(muster, text)
        if m:
            return deutsch.format(*m.groups())
    return text


# ---------------------------------------------------------------------------
# Vergleich
# ---------------------------------------------------------------------------
def _norm(v):
    if isinstance(v, float):
        v = round(v, 2)
        if v == int(v):
            return int(v)
    return v


def _sortkey(zeile):
    return tuple((x is None, type(x).__name__ in ("int", "float"), str(x) if not isinstance(x, (int, float)) else "", x if isinstance(x, (int, float)) else 0) for x in zeile)


def hat_order_by(sql):
    """True, wenn die letzte Anweisung auf oberster Ebene ein ORDER BY hat."""
    teile = zerlege(sql)
    if not teile:
        return False
    s = _ohne_kommentare(teile[-1])
    s = re.sub(r"'(?:[^']|'')*'", "''", s)
    tiefe, oben = 0, []
    for z in s:
        if z == "(":
            tiefe += 1
        elif z == ")":
            tiefe -= 1
        elif tiefe == 0:
            oben.append(z)
    return re.search(r"\bORDER\s+BY\b", "".join(oben), re.I) is not None


def vergleiche(ist, soll, sortiert=False, spalten_pruefen=False):
    """Gibt (ok, meldung) zurück."""
    if not ist.hat_tabelle:
        return False, "Deine Eingabe hat keine Tabelle zurückgegeben (fehlt ein SELECT?)."
    if len(ist.spalten) != len(soll.spalten):
        return False, (f"Du lieferst {len(ist.spalten)} Spalte(n), erwartet werden {len(soll.spalten)}: "
                       f"{', '.join(soll.spalten)}")
    if spalten_pruefen:
        falsch = [(a, b) for a, b in zip(ist.spalten, soll.spalten) if a.lower() != b.lower()]
        if falsch:
            return False, "Spaltennamen stimmen nicht: " + ", ".join(f"'{a}' sollte '{b}' heißen" for a, b in falsch)
    a = [tuple(_norm(v) for v in z) for z in ist.zeilen]
    b = [tuple(_norm(v) for v in z) for z in soll.zeilen]
    if len(a) != len(b):
        return False, f"Du lieferst {len(a)} Zeile(n), erwartet werden {len(b)}."
    if sorted(a, key=_sortkey) != sorted(b, key=_sortkey):
        # Spaltenreihenfolge vertauscht?
        if sorted(map(sorted_tuple, a)) == sorted(map(sorted_tuple, b)):
            return False, "Die Werte stimmen, aber die Spalten-Reihenfolge ist anders als verlangt."
        return False, "Anzahl Zeilen/Spalten stimmt, aber die Werte sind anders."
    if sortiert and a != b:
        return False, "Richtige Zeilen – aber die Reihenfolge (ORDER BY) stimmt nicht."
    return True, ""


def sorted_tuple(z):
    return tuple(sorted((str(x) for x in z)))


# ---------------------------------------------------------------------------
# Ausgabe
# ---------------------------------------------------------------------------
def _zelle(v):
    if v is None:
        return "NULL"
    if isinstance(v, float):
        v = round(v, 4)
    s = str(v).replace("\n", " ")
    return s if len(s) <= 60 else s[:57] + "..."


def tabelle_text(spalten, zeilen, max_zeilen=MAX_ZEILEN_ANZEIGE, farbig=True):
    if not spalten:
        return ""
    zeilen = list(zeilen)
    gezeigt = zeilen[:max_zeilen]
    zellen = [[_zelle(v) for v in z] for z in gezeigt]
    breiten = [max([len(str(s))] + [len(z[i]) for z in zellen]) for i, s in enumerate(spalten)]
    linie = "+" + "+".join("-" * (b + 2) for b in breiten) + "+"
    kopf = "|" + "|".join(" " + (farbe(str(s).ljust(b), F.FETT, F.GELB) if farbig else str(s).ljust(b)) + " "
                          for s, b in zip(spalten, breiten)) + "|"
    out = [linie, kopf, linie]
    for roh, z in zip(gezeigt, zellen):
        teile = []
        for v, s, b in zip(roh, z, breiten):
            txt = s.rjust(b) if isinstance(v, (int, float)) else s.ljust(b)
            if v is None and farbig:
                txt = farbe(txt, F.DIM)
            teile.append(" " + txt + " ")
        out.append("|" + "|".join(teile) + "|")
    out.append(linie)
    rest = len(zeilen) - len(gezeigt)
    info = f"{len(zeilen)} Zeile(n)" + (f" – {rest} weitere nicht angezeigt" if rest > 0 else "")
    out.append(farbe(info, F.DIM) if farbig else info)
    return "\n".join(out)


def ergebnis_text(erg):
    teile = [farbe("  " + m, F.DIM) for m in erg.meldungen]
    if erg.hat_tabelle:
        teile.append(tabelle_text(erg.spalten, erg.zeilen))
    if erg.fehler:
        teile.append(farbe("FEHLER: ", F.ROT, F.FETT) + farbe(erg.fehler, F.ROT))
        if erg.roh_fehler and erg.roh_fehler != erg.fehler:
            teile.append(farbe(f"  (Original: {erg.roh_fehler})", F.DIM))
    return "\n".join(teile)


def schema_text(conn, tabelle):
    erg = ausfuehren(conn, f"DESCRIBE {tabelle};")
    if not erg.zeilen:
        return farbe(f"Tabelle '{tabelle}' gibt es nicht.", F.ROT)
    out = [farbe(f"Struktur von {tabelle}:", F.FETT), tabelle_text(erg.spalten, erg.zeilen)]
    fks = conn.execute(f"SELECT \"from\", \"table\", \"to\", on_delete FROM pragma_foreign_key_list('{tabelle}')").fetchall()
    for von, tab, nach, od in fks:
        out.append(farbe(f"  Fremdschlüssel: {von} → {tab}({nach})" + (f"  ON DELETE {od}" if od != "NO ACTION" else ""), F.CYAN))
    daten = ausfuehren(conn, f"SELECT * FROM {tabelle} LIMIT 5;")
    if daten.hat_tabelle:
        out += [farbe("Erste 5 Zeilen:", F.FETT), tabelle_text(daten.spalten, daten.zeilen)]
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Aufgaben prüfen
# ---------------------------------------------------------------------------
def pruefe_aufgabe(aufgabe, user_sql):
    """Prüft eine Aufgabe. Rückgabe: (ok, meldung, ist_text)."""
    ok, meldung, erg = pruefe_aufgabe_roh(aufgabe, user_sql)
    return ok, meldung, ergebnis_text(erg)


def pruefe_aufgabe_roh(aufgabe, user_sql):
    """Wie pruefe_aufgabe, liefert aber das Ergebnis-Objekt statt Text."""
    typ = aufgabe.get("typ", "abfrage")
    setup = aufgabe.get("setup")
    ohne = _ohne_kommentare(user_sql)
    for wort in aufgabe.get("muss_enthalten", []):
        if not re.search(r"\b" + re.escape(wort).replace(r"\ ", r"\s+") + r"\b", ohne, re.I):
            erg = ausfuehren(neue_db(setup), user_sql)
            return False, f"Diese Aufgabe soll mit {wort} gelöst werden.", erg
    if typ == "abfrage":
        soll = ausfuehren(neue_db(setup), aufgabe["loesung"])
        ist = ausfuehren(neue_db(setup), user_sql)
        if ist.fehler:
            return False, "", ist
        sortiert = aufgabe.get("sortiert", hat_order_by(aufgabe["loesung"]))
        ok, msg = vergleiche(ist, soll, sortiert, aufgabe.get("spalten", False))
        if ok and aufgabe.get("plan"):
            p_ist, p_soll = plan(neue_db(setup), user_sql), plan(neue_db(setup), aufgabe["loesung"])
            if sorted(p_ist.zeilen or []) != sorted(p_soll.zeilen or []):
                return False, ("Das Ergebnis stimmt, aber die Datenbank kann für deine Abfrage den Index nicht nutzen.\n"
                               "  Dein Plan:     " + " | ".join(z[0] for z in p_ist.zeilen or []) +
                               "\n  Gewünschter Plan: " + " | ".join(z[0] for z in p_soll.zeilen or [])), ist
        return ok, msg, ist

    # typ == "aendern": Zustand der DB nach der Anweisung vergleichen
    db_ist, db_soll = neue_db(setup), neue_db(setup)
    ist = ausfuehren(db_ist, user_sql)
    if ist.fehler and not aufgabe.get("fehler_erlaubt"):
        return False, "", ist
    soll = ausfuehren(db_soll, aufgabe["loesung"])
    if soll.fehler and not aufgabe.get("fehler_erlaubt"):
        return False, f"(Interner Fehler in der Musterlösung: {soll.fehler})", ist
    for test_sql in _liste(aufgabe.get("tests")):
        a_ok = not ausfuehren(db_ist, test_sql).fehler
        b_ok = not ausfuehren(db_soll, test_sql).fehler
        if a_ok != b_ok:
            soll_txt = "ERLAUBT sein" if b_ok else "ABGELEHNT werden"
            ist_txt = "wurde abgelehnt" if not a_ok else "ging durch"
            return False, f"Test: {test_sql}\n  → sollte {soll_txt}, {ist_txt} aber.", ist
    for pruef_sql in _liste(aufgabe.get("pruefung")):
        a, b = kontrolle(db_ist, pruef_sql), kontrolle(db_soll, pruef_sql)
        if a.fehler:
            return False, f"Kontrollabfrage schlägt fehl: {a.fehler}\n  Kontrolle: {pruef_sql}", ist
        ok, msg = vergleiche(a, b, hat_order_by(pruef_sql))
        if not ok:
            return False, f"Die Datenbank sieht danach nicht richtig aus. {msg}\n  Kontrolle: {pruef_sql}", ist
    return True, "", ist


def kontrolle(conn, pruef_sql):
    """Kontrollabfrage. 'PLAN <select>' liefert den Ausführungsplan ohne Index-Namen."""
    if pruef_sql.upper().startswith("PLAN "):
        return plan(conn, pruef_sql[5:])
    return ausfuehren(conn, pruef_sql)


def plan(conn, sql):
    letzte = (zerlege(sql) or [""])[-1]
    letzte = re.sub(r"^\s*EXPLAIN\s+(QUERY\s+PLAN\s+)?", "", uebersetze(letzte)[0] or "", flags=re.I)
    erg = ausfuehren(conn, "EXPLAIN QUERY PLAN " + letzte)
    if erg.hat_tabelle:
        erg.spalten = ["plan"]
        erg.zeilen = [(re.sub(r"USING (COVERING )?INDEX \S+", "USING INDEX", z[-1]),) for z in erg.zeilen]
    return erg


def erwartet(aufgabe):
    """Was als Ergebnis erwartet wird: Liste von (titel, Ergebnis). Leer, wenn nur Tests prüfen."""
    if aufgabe.get("typ", "abfrage") == "abfrage":
        return [("Erwartetes Ergebnis", ausfuehren(neue_db(aufgabe.get("setup")), aufgabe["loesung"]))]
    conn = neue_db(aufgabe.get("setup"))
    ausfuehren(conn, aufgabe["loesung"])
    for test_sql in _liste(aufgabe.get("tests")):
        ausfuehren(conn, test_sql)
    return [(q, kontrolle(conn, q)) for q in _liste(aufgabe.get("pruefung"))]


def _liste(x):
    if x is None:
        return []
    return [x] if isinstance(x, str) else list(x)
