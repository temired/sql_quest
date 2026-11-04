KAPITEL = {
    "nr": 8,
    "titel": "Subqueries",
    "lektionen": [
        {
            "titel": "Skalare Unterabfragen",
            "theorie": """
                # Eine Abfrage in der Abfrage
                Frage: "Welche Spieler sind besser als der Durchschnitt?"
                Den Durchschnitt kennen wir nicht – also lassen wir ihn berechnen:

                    SELECT spieler_name, level
                    FROM spieler
                    WHERE level > (SELECT AVG(level) FROM spieler);

                * Die innere Abfrage steht in Klammern und wird zuerst ausgeführt.
                * SKALAR = sie liefert genau EINEN Wert (1 Zeile, 1 Spalte) → man kann mit `=`, `>`, `<` vergleichen.
                * `WHERE level > AVG(level)` geht NICHT (Aggregat im WHERE) – darum die Unterabfrage.
                ---
                # Unterabfrage im SELECT
                    SELECT spieler_name, level,
                           (SELECT MAX(level) FROM spieler) - level AS abstand_zum_besten
                    FROM spieler;
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige spieler_name und level aller Spieler, deren Level ÜBER dem Durchschnittslevel liegt.",
                    "loesung": "SELECT spieler_name, level FROM spieler WHERE level > (SELECT AVG(level) FROM spieler);",
                    "hinweise": ["WHERE level > (SELECT AVG(level) FROM spieler)"],
                },
                {
                    "aufgabe": "Welcher Gegenstand ist der wertvollste? Zeige name und wert (ohne LIMIT, mit Unterabfrage).",
                    "loesung": "SELECT name, wert FROM gegenstaende WHERE wert = (SELECT MAX(wert) FROM gegenstaende);",
                    "muss_enthalten": ["MAX"],
                },
                {
                    "aufgabe": "Zeige spieler_name, level und `abstand` = wie viele Level dem Spieler bis zum höchsten Level fehlen.",
                    "loesung": "SELECT spieler_name, level, (SELECT MAX(level) FROM spieler) - level AS abstand FROM spieler;",
                    "spalten": True,
                },
                {
                    "aufgabe": "Zeige titel und belohnung_gold aller Quests, deren Belohnung mehr als doppelt so hoch ist wie die durchschnittliche Belohnung.",
                    "loesung": "SELECT titel, belohnung_gold FROM quests WHERE belohnung_gold > 2 * (SELECT AVG(belohnung_gold) FROM quests);",
                },
            ],
        },
        {
            "titel": "IN und NOT IN",
            "theorie": """
                # Unterabfrage, die eine LISTE liefert
                    SELECT spieler_name FROM spieler
                    WHERE spieler_id IN (SELECT spieler_id FROM inventar WHERE gegenstand_id = 1);
                → alle Spieler, die einen Heiltrank besitzen.

                Unterabfragen lassen sich schachteln:
                    WHERE spieler_id IN (
                        SELECT spieler_id FROM inventar
                        WHERE gegenstand_id IN (SELECT gegenstand_id FROM gegenstaende WHERE typ = 'Waffe'))
                ---
                # ⚠ Die NOT-IN-NULL-Falle (fiese Prüfungsfrage!)
                    SELECT name FROM monster
                    WHERE monster_id NOT IN (SELECT ziel_monster_id FROM quests);

                Steht in der Liste auch nur EIN NULL (Quest 'Kräuter sammeln' hat kein Zielmonster),
                liefert NOT IN IMMER 0 Zeilen! Denn `5 NOT IN (1, 2, NULL)` heißt `5<>1 AND 5<>2 AND 5<>NULL`
                → TRUE AND TRUE AND UNKNOWN → UNKNOWN.

                Lösung: NULLs ausschließen …
                    WHERE monster_id NOT IN (SELECT ziel_monster_id FROM quests WHERE ziel_monster_id IS NOT NULL)
                … oder NOT EXISTS benutzen (nächste Lektion).
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige spieler_name aller Spieler, die einen Gegenstand mit Seltenheit 'Legendär' im Inventar haben (nur Unterabfragen, kein JOIN).",
                    "loesung": """SELECT spieler_name FROM spieler WHERE spieler_id IN
                        (SELECT spieler_id FROM inventar WHERE gegenstand_id IN
                            (SELECT gegenstand_id FROM gegenstaende WHERE seltenheit = 'Legendär'));""",
                    "hinweise": ["Von innen nach außen: Legendäre gegenstand_ids → spieler_ids im inventar → Namen.",
                                 "WHERE spieler_id IN (SELECT spieler_id FROM inventar WHERE gegenstand_id IN (SELECT ...))"],
                },
                {
                    "aufgabe": "Zeige name aller Gegenstände, die NIEMAND im Inventar hat (NOT IN).",
                    "loesung": "SELECT name FROM gegenstaende WHERE gegenstand_id NOT IN (SELECT gegenstand_id FROM inventar);",
                },
                {
                    "aufgabe": """
                        Ein neues Monster 'Mimik' ist aufgetaucht (Setup hat es eingefügt), für das es noch keine Quest gibt.
                        Zeige name aller Monster, für die es KEINE Quest gibt. Vorsicht, NULL-Falle!
                    """,
                    "setup": "INSERT INTO monster (name, gebiet, stufe, ist_boss) VALUES ('Mimik', 'Verlassene Gruft', 7, 0);",
                    "loesung": "SELECT name FROM monster WHERE monster_id NOT IN (SELECT ziel_monster_id FROM quests WHERE ziel_monster_id IS NOT NULL);",
                    "falsch": ["SELECT name FROM monster WHERE monster_id NOT IN (SELECT ziel_monster_id FROM quests);"],
                    "hinweise": ["Probier erst die naive Variante – 0 Zeilen! Warum?",
                                 "In der Unterabfrage: WHERE ziel_monster_id IS NOT NULL"],
                },
            ],
        },
        {
            "titel": "EXISTS & korrelierte Unterabfragen",
            "theorie": """
                # Korrelierte Unterabfrage = bezieht sich auf die äußere Zeile
                    SELECT g.gildenname
                    FROM gilden g
                    WHERE EXISTS (SELECT 1 FROM spieler s WHERE s.gilde_id = g.gilde_id);

                * Die innere Abfrage benutzt `g.gilde_id` von außen → sie läuft (gedanklich) für JEDE Gilde neu.
                * `g` und `s` sind Tabellen-Aliase (Spitznamen), damit klar ist, welche Tabelle gemeint ist.
                * `EXISTS (...)` ist TRUE, sobald die Unterabfrage mindestens 1 Zeile liefert.
                  Was im SELECT steht, ist egal – üblich ist `SELECT 1`.
                * `NOT EXISTS` ist die sichere Alternative zu NOT IN (keine NULL-Falle).
                ---
                # Korreliert vergleichen
                "Spieler, die besser sind als der Durchschnitt IHRER Klasse":
                    SELECT s.spieler_name, s.klasse, s.level
                    FROM spieler s
                    WHERE s.level > (SELECT AVG(s2.level) FROM spieler s2 WHERE s2.klasse = s.klasse);

                ! ANY / ALL (MySQL, nicht SQLite):
                !   `WHERE level > ALL (SELECT level FROM spieler WHERE klasse = 'Magier')` = höher als JEDER Magier
                !   `WHERE level > ANY (SELECT ...)` = höher als MINDESTENS EIN Magier
                ! Gleichwertig: `> (SELECT MAX(...))` bzw. `> (SELECT MIN(...))`.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige gildenname aller Gilden, die mindestens ein Mitglied haben (EXISTS).",
                    "loesung": "SELECT g.gildenname FROM gilden g WHERE EXISTS (SELECT 1 FROM spieler s WHERE s.gilde_id = g.gilde_id);",
                    "muss_enthalten": ["EXISTS"],
                },
                {
                    "aufgabe": "Zeige gildenname und gruendungsjahr aller Gilden OHNE Mitglieder (NOT EXISTS).",
                    "loesung": "SELECT g.gildenname, g.gruendungsjahr FROM gilden g WHERE NOT EXISTS (SELECT 1 FROM spieler s WHERE s.gilde_id = g.gilde_id);",
                    "muss_enthalten": ["NOT EXISTS"],
                },
                {
                    "aufgabe": "Zeige spieler_name, klasse, level aller Spieler, deren Level über dem Durchschnitt IHRER EIGENEN Klasse liegt.",
                    "loesung": "SELECT s.spieler_name, s.klasse, s.level FROM spieler s WHERE s.level > (SELECT AVG(s2.level) FROM spieler s2 WHERE s2.klasse = s.klasse);",
                    "hinweise": ["Zwei Aliase für dieselbe Tabelle: spieler s außen, spieler s2 innen.",
                                 "WHERE s2.klasse = s.klasse"],
                },
                {
                    "aufgabe": "Zeige für jeden Gegenstand name und `im_umlauf` = Summe der anzahl aus dem Inventar (korrelierte Unterabfrage im SELECT). Wo nichts im Umlauf ist, darf NULL stehen.",
                    "loesung": "SELECT g.name, (SELECT SUM(i.anzahl) FROM inventar i WHERE i.gegenstand_id = g.gegenstand_id) AS im_umlauf FROM gegenstaende g;",
                    "spalten": True,
                },
                {
                    "aufgabe": "Zeige spieler_name und level aller Spieler, deren Level höher ist als das JEDES Magiers (ohne ALL – mit MAX).",
                    "loesung": "SELECT spieler_name, level FROM spieler WHERE level > (SELECT MAX(level) FROM spieler WHERE klasse = 'Magier');",
                },
            ],
        },
        {
            "titel": "Unterabfragen in FROM & CTEs (WITH)",
            "theorie": """
                # Abgeleitete Tabelle (Derived Table)
                Das Ergebnis einer Abfrage ist wieder eine Tabelle – also kann man daraus selektieren:
                    SELECT t.klasse, t.schnitt
                    FROM (SELECT klasse, AVG(level) AS schnitt FROM spieler GROUP BY klasse) AS t
                    WHERE t.schnitt > 10;
                ! In MySQL MUSS eine Unterabfrage im FROM einen Alias haben (Fehler 1248).
                ---
                # CTE – Common Table Expression (WITH)
                Dasselbe, aber lesbarer: Man gibt der Unterabfrage vorher einen Namen.
                    WITH klassen_schnitt AS (
                        SELECT klasse, AVG(level) AS schnitt FROM spieler GROUP BY klasse
                    )
                    SELECT klasse, schnitt FROM klassen_schnitt WHERE schnitt > 10;

                Mehrere CTEs mit Komma:  `WITH a AS (...), b AS (...) SELECT ...`
                ! CTEs gibt es in MySQL ab Version 8.0.
                ---
                # Rekursive CTE (Bonus)
                    WITH RECURSIVE zahlen(n) AS (
                        SELECT 1                              -- Startwert
                        UNION ALL
                        SELECT n + 1 FROM zahlen WHERE n < 10 -- Schritt + Abbruch
                    )
                    SELECT n FROM zahlen;
                Nützlich für Hierarchien (Chef → Mitarbeiter, Ordner → Unterordner) und Zahlenreihen.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige klasse und Durchschnittslevel (`schnitt`) aller Klassen, deren Durchschnitt über 10 liegt – mit einer Unterabfrage im FROM (nicht HAVING).",
                    "loesung": "SELECT t.klasse, t.schnitt FROM (SELECT klasse, AVG(level) AS schnitt FROM spieler GROUP BY klasse) AS t WHERE t.schnitt > 10;",
                    "spalten": True,
                    "muss_enthalten": ["FROM ("],
                },
                {
                    "aufgabe": """
                        Gleiche Frage mit einer CTE: Lege mit WITH die Tabelle `gebiet_stats` an (gebiet, max_stufe pro Gebiet)
                        und zeige daraus alle Gebiete mit max_stufe >= 10, sortiert nach max_stufe absteigend.
                    """,
                    "loesung": """WITH gebiet_stats AS (SELECT gebiet, MAX(stufe) AS max_stufe FROM monster GROUP BY gebiet)
                        SELECT gebiet, max_stufe FROM gebiet_stats WHERE max_stufe >= 10 ORDER BY max_stufe DESC;""",
                    "spalten": True,
                    "muss_enthalten": ["WITH"],
                },
                {
                    "aufgabe": "Erzeuge mit einer rekursiven CTE die Level 1 bis 10 (`level`) und die benötigten XP (`xp` = level * level * 100).",
                    "loesung": """WITH RECURSIVE stufen(level) AS (SELECT 1 UNION ALL SELECT level + 1 FROM stufen WHERE level < 10)
                        SELECT level, level * level * 100 AS xp FROM stufen;""",
                    "spalten": True,
                    "muss_enthalten": ["RECURSIVE"],
                    "hinweise": ["WITH RECURSIVE stufen(level) AS (SELECT 1 UNION ALL SELECT level + 1 FROM stufen WHERE level < 10) SELECT ..."],
                },
            ],
        },
        {
            "titel": "Unterabfragen in UPDATE, DELETE, INSERT",
            "theorie": """
                # Unterabfragen ändern Daten
                    UPDATE spieler SET level = level + 1
                    WHERE gilde_id IN (SELECT gilde_id FROM gilden WHERE gruendungsjahr < 2020);

                    DELETE FROM inventar
                    WHERE gegenstand_id IN (SELECT gegenstand_id FROM gegenstaende WHERE typ = 'Trank');

                    UPDATE gegenstaende
                    SET wert = (SELECT MAX(wert) FROM gegenstaende) WHERE name = 'Mysteriöses Amulett';

                ! MySQL-Eigenheit (Fehler 1093): Man darf in UPDATE/DELETE nicht direkt aus derselben
                ! Tabelle selektieren, die man ändert. Trick: die Unterabfrage nochmal einpacken:
                !   `... WHERE wert = (SELECT m FROM (SELECT MAX(wert) AS m FROM gegenstaende) AS t)`
            """,
            "aufgaben": [
                {
                    "typ": "aendern",
                    "aufgabe": "Alle Mitglieder von Gilden, die VOR 2020 gegründet wurden, steigen 1 Level auf.",
                    "loesung": "UPDATE spieler SET level = level + 1 WHERE gilde_id IN (SELECT gilde_id FROM gilden WHERE gruendungsjahr < 2020);",
                    "pruefung": "SELECT spieler_name, level FROM spieler",
                },
                {
                    "typ": "aendern",
                    "aufgabe": "Alle Tränke (typ 'Trank') werden aus allen Inventaren entfernt.",
                    "loesung": "DELETE FROM inventar WHERE gegenstand_id IN (SELECT gegenstand_id FROM gegenstaende WHERE typ = 'Trank');",
                    "pruefung": "SELECT inventar_id, spieler_id, gegenstand_id FROM inventar",
                },
                {
                    "typ": "aendern",
                    "aufgabe": "Das 'Mysteriöse Amulett' bekommt als Wert den aktuell HÖCHSTEN Wert aller Gegenstände.",
                    "loesung": "UPDATE gegenstaende SET wert = (SELECT MAX(wert) FROM gegenstaende) WHERE name = 'Mysteriöses Amulett';",
                    "pruefung": "SELECT name, wert FROM gegenstaende",
                },
                {
                    "typ": "aendern",
                    "aufgabe": "Jeder Spieler, der über dem Durchschnittslevel liegt, bekommt 1 Lebenselixier (gegenstand_id 9, anzahl 1) ins Inventar.",
                    "loesung": "INSERT INTO inventar (spieler_id, gegenstand_id, anzahl) SELECT spieler_id, 9, 1 FROM spieler WHERE level > (SELECT AVG(level) FROM spieler);",
                    "pruefung": "SELECT spieler_id, gegenstand_id, anzahl FROM inventar",
                },
            ],
        },
    ],
    "boss": {
        "titel": "Die Schatzkammer",
        "story": """
            # Der Drache bewacht die Schatzkammer.
            "Nenne mir die reichsten Abenteurer – aber JOINs sind hier verboten!"
            (Die kommen erst in Kapitel 10.)
        """,
        "aufgabe": """
            Berechne für jeden Spieler den Gesamtwert seines Inventars (Summe aus anzahl * wert des Gegenstands).
            Zeige spieler_name und `gesamtwert` aller Spieler, deren Gesamtwert ÜBER dem Durchschnitt
            der Gesamtwerte aller Spieler mit Inventar liegt. Sortiert nach gesamtwert absteigend, bei Gleichstand nach spieler_name.
            Nur Unterabfragen/CTEs – kein JOIN.
        """,
        "loesung": """WITH werte AS (
                SELECT i.spieler_id,
                       SUM(i.anzahl * (SELECT g.wert FROM gegenstaende g WHERE g.gegenstand_id = i.gegenstand_id)) AS gesamtwert
                FROM inventar i
                GROUP BY i.spieler_id
            )
            SELECT (SELECT s.spieler_name FROM spieler s WHERE s.spieler_id = w.spieler_id) AS spieler_name, w.gesamtwert
            FROM werte w
            WHERE w.gesamtwert > (SELECT AVG(gesamtwert) FROM werte)
            ORDER BY w.gesamtwert DESC, spieler_name;""",
        "spalten": True,
        "hinweise": ["Schritt 1 (CTE): pro spieler_id SUM(anzahl * (SELECT wert FROM gegenstaende WHERE ...)) aus inventar.",
                     "Schritt 2: WHERE gesamtwert > (SELECT AVG(gesamtwert) FROM werte)",
                     "Den Namen holst du mit einer Unterabfrage im SELECT aus spieler."],
    },
}
