"""
Ablauf einer SELECT-Abfrage Schritt für Schritt – in der logischen Reihenfolge
FROM → JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT.

Für jeden Schritt wird das Zwischenergebnis berechnet und pro Zeile markiert, was passiert:
  "raus"   – fällt in diesem Schritt weg
  "null"   – beim OUTER JOIN mit NULL aufgefüllt (kein Partner)
  "g0/g1"  – gehört zu einer Gruppe (abwechselnd, zum Einfärben)
  "drin"   – bleibt bei LIMIT übrig
"""
import re
import sqlite3

from engine import zerlege, uebersetze, ausfuehren, _ohne_kommentare

MAX_ZEILEN = 200
_AGGREGATE = r"\b(COUNT|SUM|AVG|MIN|MAX|GROUP_CONCAT|TOTAL)\s*\("


class AblaufFehler(Exception):
    pass


# ---------------------------------------------------------------------------
# Zerlegen
# ---------------------------------------------------------------------------
def _maske(sql):
    """Gleich langer Text, in dem Klammerinhalte und Strings durch Leerzeichen ersetzt sind.
    So findet man Schlüsselwörter nur auf oberster Ebene."""
    out, tiefe, quote = [], 0, None
    for z in sql:
        if quote:
            out.append(" ")
            if z == quote:
                quote = None
            continue
        if z in "'\"`":
            quote = z
            out.append(" ")
        elif z == "(":
            tiefe += 1
            out.append("(" if tiefe == 1 else " ")
        elif z == ")":
            tiefe -= 1
            out.append(")" if tiefe == 0 else " ")
        else:
            out.append(z if tiefe == 0 else " ")
    return "".join(out)


def _teile_oben(text, trenner=","):
    maske, teile, start = _maske(text), [], 0
    for i, z in enumerate(maske):
        if z == trenner:
            teile.append(text[start:i])
            start = i + 1
    return [t.strip() for t in teile + [text[start:]] if t.strip()]


_KLAUSELN = r"\b(SELECT|FROM|WHERE|GROUP\s+BY|HAVING|ORDER\s+BY|LIMIT|UNION|INTERSECT|EXCEPT|WINDOW)\b"


def zerlege_select(sql):
    """Teilt eine SELECT-Anweisung in ihre Klauseln. Rückgabe: dict."""
    sql = _ohne_kommentare(sql).strip().rstrip(";").strip()
    maske = _maske(sql)
    oben = maske.upper()
    praefix = ""
    if re.match(r"^\s*WITH\b", oben):
        m = re.search(r"\bSELECT\b", oben)
        if not m:
            raise AblaufFehler("Nach WITH fehlt das SELECT.")
        praefix, sql, maske, oben = sql[:m.start()], sql[m.start():], maske[m.start():], oben[m.start():]
    if not re.match(r"^\s*SELECT\b", oben):
        raise AblaufFehler("Den Ablauf gibt es nur für SELECT-Abfragen.")
    treffer = [(m.start(), m.end(), re.sub(r"\s+", " ", m.group(1))) for m in re.finditer(_KLAUSELN, oben)]
    for _, _, wort in treffer:
        if wort in ("UNION", "INTERSECT", "EXCEPT"):
            raise AblaufFehler(f"Bei {wort} werden zwei Abfragen zusammengeführt – zeig dir den Ablauf "
                               "für jedes SELECT einzeln an.")
        if wort == "WINDOW":
            raise AblaufFehler("WINDOW-Klauseln werden in der Ablauf-Ansicht nicht unterstützt.")
    teile = {}
    for i, (anfang, ende, wort) in enumerate(treffer):
        if wort in teile:
            raise AblaufFehler(f"{wort} kommt zweimal vor – den Ablauf gibt es nur für ein einzelnes SELECT.")
        bis = treffer[i + 1][0] if i + 1 < len(treffer) else len(sql)
        teile[wort] = sql[ende:bis].strip()
    auswahl = teile.get("SELECT", "")
    distinct = bool(re.match(r"^DISTINCT\b", auswahl, re.I))
    if distinct:
        auswahl = auswahl[8:].strip()
    elif re.match(r"^ALL\b", auswahl, re.I):
        auswahl = auswahl[3:].strip()
    return {"praefix": praefix, "select": auswahl, "distinct": distinct, "from": teile.get("FROM"),
            "where": teile.get("WHERE"), "group": teile.get("GROUP BY"), "having": teile.get("HAVING"),
            "order": teile.get("ORDER BY"), "limit": teile.get("LIMIT")}


_JOIN = re.compile(r"\b(NATURAL\s+)?(?:(LEFT|RIGHT|FULL)(?:\s+OUTER)?\s+|(INNER)\s+|(CROSS)\s+)?JOIN\b", re.I)


def zerlege_from(text):
    """Liste von Quellen: {art, quelle, bedingung, sql_bis_hier, code}."""
    maske = _maske(text)
    grenzen = []  # (start, ende, art)
    for m in _JOIN.finditer(maske):
        art = (m.group(2) or m.group(3) or m.group(4) or "INNER").upper()
        if m.group(1):
            art = "NATURAL " + art
        grenzen.append((m.start(), m.end(), art))
    for i, z in enumerate(maske):
        if z == ",":
            grenzen.append((i, i + 1, "KOMMA"))
    grenzen.sort()
    quellen = []
    anfang_teil, art = 0, "BASIS"
    for start, ende, naechste_art in grenzen + [(len(text), len(text), None)]:
        stueck, stueck_maske = text[anfang_teil:start], maske[anfang_teil:start]
        m = re.search(r"\b(ON|USING)\b", stueck_maske, re.I)
        quelle = stueck[:m.start()].strip() if m else stueck.strip()
        bedingung = stueck[m.start():].strip() if m else None
        quellen.append({"art": art, "quelle": quelle, "bedingung": bedingung, "name": _quellname(quelle),
                        "sql_bis_hier": text[:start].strip(),
                        "code": (text[grenzen_start(grenzen, anfang_teil):start].strip())})
        anfang_teil, art = ende, naechste_art
    return quellen


def grenzen_start(grenzen, anfang_teil):
    """Für die Code-Anzeige: inkl. JOIN-Schlüsselwort davor."""
    for start, ende, _ in grenzen:
        if ende == anfang_teil:
            return start
    return anfang_teil


def _quellname(quelle):
    maske = re.sub(r"\(\s*\)", "()", _maske(quelle).strip())   # Klammerinhalt zählt nicht als Wort
    teile = re.split(r"\s+", maske)
    if len(teile) == 1:
        return quelle.strip().strip("`\"")
    alias = teile[-1]
    return alias.strip("`\"") if alias.upper() != "AS" else teile[0]


def _alias_tabelle(auswahl):
    """{alias: ausdruck} aus der SELECT-Liste."""
    aliase = {}
    for teil in _teile_oben(auswahl):
        ausdruck, alias = _ausdruck_und_alias(teil)
        if alias:
            aliase[alias.lower()] = ausdruck
    return aliase


def _ausdruck_und_alias(teil):
    """'wert * 2 AS doppelt' → ('wert * 2', 'doppelt'); 'COUNT(*) anzahl' → ('COUNT(*)', 'anzahl')."""
    m = re.match(r"^(.*\S)\s+AS\s+[`\"]?([\wÄÖÜäöüß]+)[`\"]?$", teil, re.I | re.S)
    if not m:
        m = re.match(r"^(.*[\w)\]'])\s+[`\"]?([\wÄÖÜäöüß]+)[`\"]?$", teil, re.S)
        if m and m.group(2).upper() in ("END", "NULL", "ASC", "DESC"):
            m = None
    return (m.group(1), m.group(2)) if m else (teil, None)


def _hat_aggregat(auswahl):
    maske = auswahl
    for m in re.finditer(_AGGREGATE, maske, re.I):
        # schließende Klammer finden – folgt OVER, ist es eine Fensterfunktion
        tiefe, i = 0, m.end() - 1
        while i < len(maske):
            if maske[i] == "(":
                tiefe += 1
            elif maske[i] == ")":
                tiefe -= 1
                if tiefe == 0:
                    break
            i += 1
        if not re.match(r"\s*OVER\b", maske[i + 1:], re.I):
            return True
    return False


# ---------------------------------------------------------------------------
# Ausführen
# ---------------------------------------------------------------------------
def _abfrage(conn, praefix, sql):
    cur = conn.execute(praefix + sql)
    spalten = [d[0] for d in cur.description]
    return spalten, cur.fetchall()


def _spalten_von(conn, praefix, quelle):
    cur = conn.execute(f"{praefix}SELECT * FROM {quelle} LIMIT 0")
    return [d[0] for d in cur.description]


def _schritt(klausel, titel, code, text, spalten, zeilen, marken=None, extra=None):
    marken = marken or [None] * len(zeilen)
    s = {"klausel": klausel, "titel": titel, "code": code, "text": text,
         "spalten": spalten, "zeilen": [list(z) for z in zeilen[:MAX_ZEILEN]],
         "marken": marken[:MAX_ZEILEN], "anzahl": len(zeilen)}
    if extra:
        s.update(extra)
    return s


def _flag_trennen(spalten, zeilen):
    """Letzte Spalte ist ein Hilfs-Flag → (spalten, zeilen, flags)."""
    return spalten[:-1], [z[:-1] for z in zeilen], [z[-1] for z in zeilen]


def ablauf(conn, sql):
    """Berechnet alle Schritte für die LETZTE Anweisung in sql (vorherige werden einfach ausgeführt)."""
    anweisungen = zerlege(sql)
    if not anweisungen:
        raise AblaufFehler("Erst eine SELECT-Abfrage schreiben.")
    if len(anweisungen) > 1:
        vorher = ausfuehren(conn, "\n".join(anweisungen[:-1]))
        if vorher.fehler:
            raise AblaufFehler(f"Fehler in den Anweisungen davor: {vorher.fehler}")
    if not re.match(r"^\s*(SELECT|WITH)\b", _ohne_kommentare(anweisungen[-1]), re.I):
        raise AblaufFehler("Den Ablauf gibt es nur für SELECT-Abfragen (die letzte Anweisung im Editor).")
    letzte, hinweis = uebersetze(anweisungen[-1])
    if letzte is None:
        raise AblaufFehler(hinweis or "Diese Anweisung hat keinen Ablauf.")
    probe = ausfuehren(conn, letzte + ";")
    if probe.fehler:
        raise AblaufFehler(probe.fehler)

    k = zerlege_select(letzte)
    p = k["praefix"]
    schritte = []
    ausgabe = ("DISTINCT " if k["distinct"] else "") + k["select"]

    def teil(select, *, where=True, group=True, having=True, order=False, limit=False, distinct=False):
        s = "SELECT " + ("DISTINCT " if distinct else "") + select
        if k["from"]:
            s += " FROM " + k["from"]
        if where and k["where"]:
            s += " WHERE " + k["where"]
        if group and k["group"]:
            s += " GROUP BY " + k["group"]
        if having and k["having"]:
            s += " HAVING " + k["having"]
        if order and k["order"]:
            s += " ORDER BY " + k["order"]
        if limit and k["limit"]:
            s += " LIMIT " + k["limit"]
        return s

    # ---- FROM + JOINs ------------------------------------------------------
    alle_spalten = "*"
    if k["from"]:
        quellen = zerlege_from(k["from"])
        mehrere = len(quellen) > 1
        bisher = []  # (qualifizierer, [spalten])
        vorher_anzahl = None
        for i, q in enumerate(quellen):
            spalten_q = _spalten_von(conn, p, q["quelle"])
            bisher.append((q["name"], spalten_q))
            liste = ", ".join(f'{n}."{c}" AS "{n + "." + c if mehrere else c}"' for n, cs in bisher for c in cs)
            von = q["sql_bis_hier"]
            if i == 0:
                spalten, zeilen = _abfrage(conn, p, f"SELECT {liste} FROM {von}")
                text = (f"FROM holt ALLE Zeilen aus {q['quelle']} – {len(zeilen)} Zeilen. "
                        "Noch ist nichts gefiltert oder sortiert.")
                if mehrere:
                    text += " Die Spaltennamen zeigen hier, aus welcher Tabelle sie kommen."
                schritte.append(_schritt("FROM", "Tabelle holen", "FROM " + q["code"], text, spalten, zeilen))
            else:
                art = q["art"]
                null_check = None
                if art in ("LEFT", "FULL"):
                    null_check = " AND ".join(f'{q["name"]}."{c}" IS NULL' for c in spalten_q)
                if art == "RIGHT":
                    null_check = " AND ".join(f'{n}."{c}" IS NULL' for n, cs in bisher[:-1] for c in cs)
                if art == "FULL":
                    links = " AND ".join(f'{n}."{c}" IS NULL' for n, cs in bisher[:-1] for c in cs)
                    null_check = f"({null_check}) OR ({links})"
                flag = f", CASE WHEN {null_check} THEN 1 ELSE 0 END" if null_check else ""
                spalten, zeilen = _abfrage(conn, p, f"SELECT {liste}{flag} FROM {von}")
                marken = None
                aufgefuellt = 0
                if null_check:
                    spalten, zeilen, flags = _flag_trennen(spalten, zeilen)
                    marken = ["null" if f else None for f in flags]
                    aufgefuellt = sum(flags)
                text = _join_text(art, q, vorher_anzahl, len(zeilen), aufgefuellt, len(_abfrage(conn, p, f"SELECT 1 FROM {q['quelle']}")[1]))
                schritte.append(_schritt("JOIN", f"{art.title() if art != 'KOMMA' else 'Komma'}-Join mit {q['name']}",
                                         q["code"], text, spalten, zeilen, marken))
            vorher_anzahl = len(zeilen)
        alle_spalten = ", ".join(f'{n}."{c}" AS "{n + "." + c if mehrere else c}"' for n, cs in bisher for c in cs)

    # ---- WHERE ---------------------------------------------------------------
    if k["where"] and k["from"]:
        try:
            spalten, zeilen = _abfrage(conn, p, f"SELECT {alle_spalten}, CASE WHEN ({k['where']}) THEN 1 ELSE 0 END"
                                                 f" FROM {k['from']}")
        except sqlite3.Error:
            raise AblaufFehler("WHERE benutzt etwas, das es an dieser Stelle noch nicht gibt – z.B. einen Alias aus dem "
                               "SELECT oder eine Aggregatfunktion. In MySQL wäre das ein Fehler (Aggregate → HAVING).")
        spalten, zeilen, flags = _flag_trennen(spalten, zeilen)
        bleiben = sum(flags)
        schritte.append(_schritt(
            "WHERE", "Zeilen filtern", "WHERE " + k["where"],
            f"WHERE prüft JEDE Zeile einzeln. Ist die Bedingung nicht WAHR (also falsch oder NULL), fliegt die Zeile "
            f"raus (✘ / rot durchgestrichen). {bleiben} von {len(zeilen)} Zeilen bleiben.",
            spalten, zeilen, [None if f else "raus" for f in flags]))

    # ---- GROUP BY ------------------------------------------------------------
    aliase = _alias_tabelle(k["select"])
    if k["group"] and k["from"]:
        schluessel = []
        auswahl_teile = _teile_oben(k["select"])
        for ausdruck in _teile_oben(k["group"]):
            if ausdruck.isdigit() and 1 <= int(ausdruck) <= len(auswahl_teile):   # GROUP BY 1 = erste SELECT-Spalte
                schluessel.append(_ausdruck_und_alias(auswahl_teile[int(ausdruck) - 1])[0])
            elif re.fullmatch(r"[`\"]?[\wÄÖÜäöüß]+[`\"]?", ausdruck):           # GROUP BY alias
                schluessel.append(aliase.get(ausdruck.strip("`\"").lower(), ausdruck))
            else:
                schluessel.append(ausdruck)
        kopf = ", ".join(f'{a} AS "▶ {_teile_oben(k["group"])[i]}"' for i, a in enumerate(schluessel))
        where = f" WHERE {k['where']}" if k["where"] else ""
        von = f" FROM {k['from']}" if k["from"] else ""
        spalten, zeilen = _abfrage(conn, p, f"SELECT {kopf}, {alle_spalten}{von}{where} ORDER BY "
                                            + ", ".join(str(i + 1) for i in range(len(schluessel))))
        gruppen, marken, letzter = 0, [], object()
        for z in zeilen:
            key = tuple(z[:len(schluessel)])
            if key != letzter:
                gruppen += 1
                letzter = key
            marken.append(f"g{(gruppen - 1) % 2}")
        schritte.append(_schritt(
            "GROUP BY", "Gruppen bilden", "GROUP BY " + k["group"],
            f"GROUP BY packt alle Zeilen mit gleichem Wert in ▶ {k['group']} in einen \"Eimer\": {gruppen} Gruppen "
            "(abwechselnd eingefärbt bzw. ▌▐ markiert). Ab jetzt wird pro Gruppe gerechnet – am Ende gibt es pro Gruppe genau EINE Zeile.",
            spalten, zeilen, marken))

    # ---- HAVING --------------------------------------------------------------
    if k["having"]:
        spalten, zeilen = _abfrage(conn, p, teil(f"{k['select']}, CASE WHEN ({k['having']}) THEN 1 ELSE 0 END",
                                                 having=False))
        spalten, zeilen, flags = _flag_trennen(spalten, zeilen)
        schritte.append(_schritt(
            "HAVING", "Gruppen filtern", "HAVING " + k["having"],
            f"HAVING prüft jede GRUPPE (nicht jede Zeile) – deshalb darf hier COUNT, SUM & Co. stehen. "
            f"{sum(flags)} von {len(zeilen)} Gruppen bleiben, der Rest ist markiert (✘ / rot durchgestrichen).",
            spalten, zeilen, [None if f else "raus" for f in flags]))

    # ---- SELECT --------------------------------------------------------------
    spalten, zeilen = _abfrage(conn, p, teil(k["select"]))
    text = "SELECT berechnet jetzt erst die Ausgabespalten"
    if aliase:
        text += f" und vergibt die Aliase ({', '.join(aliase)}). Darum kennt WHERE diese Namen noch nicht – ORDER BY schon"
    text += "."
    if not k["group"] and _hat_aggregat(k["select"]):
        text += (" Hier steht eine Aggregatfunktion ohne GROUP BY: Die ganze (gefilterte) Tabelle zählt als EINE Gruppe "
                 "→ genau eine Ergebniszeile.")
    elif k["group"]:
        text += f" Aus jeder Gruppe wird genau eine Zeile – {len(zeilen)} Zeilen."
    schritte.append(_schritt("SELECT", "Spalten auswählen & berechnen", "SELECT " + ausgabe, text, spalten, zeilen))

    # ---- DISTINCT ------------------------------------------------------------
    if k["distinct"]:
        vorher = len(zeilen)
        spalten, zeilen = _abfrage(conn, p, teil(k["select"], distinct=True))
        schritte.append(_schritt("DISTINCT", "Duplikate entfernen", "SELECT DISTINCT",
                                 f"DISTINCT entfernt Zeilen, die in ALLEN Spalten gleich sind: aus {vorher} werden "
                                 f"{len(zeilen)} Zeilen.", spalten, zeilen))

    # ---- ORDER BY ------------------------------------------------------------
    if k["order"]:
        spalten, zeilen = _abfrage(conn, p, teil(k["select"], order=True, distinct=k["distinct"]))
        schritte.append(_schritt("ORDER BY", "Sortieren", "ORDER BY " + k["order"],
                                 f"ORDER BY sortiert das fertige Ergebnis nach {k['order']}. "
                                 "Erst hier gibt es eine garantierte Reihenfolge – ohne ORDER BY ist sie zufällig.",
                                 spalten, zeilen))

    # ---- LIMIT ---------------------------------------------------------------
    if k["limit"]:
        anzahl, offset = _limit_werte(k["limit"])
        if anzahl is not None:
            marken = ["drin" if offset <= i < offset + anzahl else "raus" for i in range(len(zeilen))]
            text = (f"LIMIT behält nur {anzahl} Zeile(n)"
                    + (f", nachdem die ersten {offset} übersprungen wurden (OFFSET)" if offset else "")
                    + " – grün bzw. ✔ markiert. Der Rest fällt weg.")
            if not k["order"]:
                text += " Achtung: Ohne ORDER BY ist nicht festgelegt, WELCHE Zeilen das sind!"
            schritte.append(_schritt("LIMIT", "Abschneiden", "LIMIT " + k["limit"], text, spalten, zeilen, marken))

    ende = ausfuehren(conn, letzte + ";")
    schritte.append(_schritt("ERGEBNIS", "Endergebnis", "", f"Das ist das Ergebnis deiner Abfrage: {len(ende.zeilen or [])} Zeile(n).",
                             ende.spalten or [], ende.zeilen or []))
    return schritte


def _join_text(art, q, vorher, nachher, aufgefuellt, rechts):
    name = q["quelle"]
    bed = q["bedingung"] or ""
    if art in ("KOMMA", "CROSS"):
        t = (f"Jede Zeile von bisher ({vorher}) wird mit JEDER Zeile aus {name} ({rechts}) kombiniert: "
             f"{vorher} × {rechts} = {nachher} Zeilen (kartesisches Produkt).")
        if art == "KOMMA":
            t += " Die eigentliche Verknüpfung passiert erst im WHERE."
        return t
    t = f"{bed}: Jede Zeile von bisher wird mit den Zeilen aus {name} verbunden, für die die Bedingung WAHR ist. "
    if art.endswith("INNER") or art == "INNER":
        t += f"Zeilen ohne Partner fallen weg. Vorher {vorher} Zeilen, jetzt {nachher}."
    elif art.endswith("LEFT"):
        t += (f"LEFT JOIN behält ALLE Zeilen von links – auch ohne Partner. Bei {aufgefuellt} Zeile(n) gab es keinen "
              f"Partner, deren {name}-Spalten sind mit NULL aufgefüllt (gelb / ∅). Jetzt {nachher} Zeilen.")
    elif art.endswith("RIGHT"):
        t += (f"RIGHT JOIN behält ALLE Zeilen aus {name} – auch ohne Partner. Bei {aufgefuellt} Zeile(n) gab es links "
              f"keinen Partner, diese Spalten sind NULL (gelb / ∅). Jetzt {nachher} Zeilen.")
    elif art.endswith("FULL"):
        t += (f"FULL JOIN behält ALLE Zeilen von beiden Seiten. {aufgefuellt} Zeile(n) ohne Partner, mit NULL aufgefüllt (gelb / ∅). "
              f"Jetzt {nachher} Zeilen.")
    if nachher > (vorher or 0) and not art.endswith(("LEFT", "RIGHT", "FULL")):
        t += " Es sind MEHR Zeilen als vorher, weil eine Zeile mehrere Partner haben kann."
    return t


def _limit_werte(text):
    m = re.fullmatch(r"\s*(\d+)\s*,\s*(\d+)\s*", text)
    if m:
        return int(m.group(2)), int(m.group(1))
    m = re.fullmatch(r"\s*(\d+)(?:\s+OFFSET\s+(\d+))?\s*", text, re.I)
    if m:
        return int(m.group(1)), int(m.group(2) or 0)
    return None, 0
