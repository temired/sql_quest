KAPITEL = {
    "nr": 7,
    "titel": "Aggregations",
    "lektionen": [
        {
            "titel": "Aggregatfunktionen",
            "theorie": """
                # Viele Zeilen → ein Wert
                    Funktion          | liefert
                    ------------------+-------------------------------------------
                    COUNT(*)          | Anzahl Zeilen
                    COUNT(spalte)     | Anzahl Zeilen, in denen spalte NICHT NULL ist
                    COUNT(DISTINCT s) | Anzahl verschiedener Werte (ohne NULL)
                    SUM(spalte)       | Summe
                    AVG(spalte)       | Durchschnitt
                    MIN / MAX(spalte) | kleinster / größter Wert (auch Texte, Datum)

                    SELECT COUNT(*) AS anzahl, ROUND(AVG(level), 2) AS schnitt FROM spieler;

                # ⚠ NULL wird von Aggregaten IGNORIERT
                * `COUNT(*)` zählt 18 Spieler, `COUNT(gilde_id)` nur 15 (3 haben NULL).
                * `AVG(wert)` teilt durch die Anzahl der Nicht-NULL-Werte!
                * SUM über 0 Zeilen ergibt NULL, nicht 0 (→ `COALESCE(SUM(x), 0)`).
            """,
            "aufgaben": [
                {
                    "aufgabe": "Wie viele Spieler gibt es? Spalte `anzahl_spieler`.",
                    "loesung": "SELECT COUNT(*) AS anzahl_spieler FROM spieler;",
                    "spalten": True,
                },
                {
                    "aufgabe": "Wie viele Spieler sind in einer Gilde? Zähle die gilde_id-Spalte (NULL zählt nicht mit). Spalte `mit_gilde`.",
                    "loesung": "SELECT COUNT(gilde_id) AS mit_gilde FROM spieler;",
                    "spalten": True,
                },
                {
                    "aufgabe": "Wie viele verschiedene Klassen gibt es? Spalte `klassen`.",
                    "loesung": "SELECT COUNT(DISTINCT klasse) AS klassen FROM spieler;",
                    "spalten": True,
                },
                {
                    "aufgabe": "Zeige das Durchschnittslevel aller Spieler, gerundet auf 2 Stellen (`schnitt`), sowie das kleinste (`min_level`) und größte Level (`max_level`).",
                    "loesung": "SELECT ROUND(AVG(level), 2) AS schnitt, MIN(level) AS min_level, MAX(level) AS max_level FROM spieler;",
                    "spalten": True,
                },
                {
                    "aufgabe": """
                        Quest-Statistik in EINER Zeile: Anzahl Quests (`anzahl`), Summe aller Belohnungen (`gesamt`),
                        kleinste (`min_gold`) und größte Belohnung (`max_gold`), Durchschnitt auf ganze Zahl gerundet (`schnitt`).
                    """,
                    "loesung": """SELECT COUNT(*) AS anzahl, SUM(belohnung_gold) AS gesamt, MIN(belohnung_gold) AS min_gold,
                        MAX(belohnung_gold) AS max_gold, ROUND(AVG(belohnung_gold)) AS schnitt FROM quests;""",
                    "spalten": True,
                },
                {
                    "aufgabe": "Wie hoch ist die durchschnittliche Stufe der BOSS-Monster? Spalte `boss_schnitt`.",
                    "loesung": "SELECT AVG(stufe) AS boss_schnitt FROM monster WHERE ist_boss = 1;",
                    "spalten": True,
                },
            ],
        },
        {
            "titel": "GROUP BY",
            "theorie": """
                # Pro Gruppe ein Ergebnis
                    SELECT klasse, COUNT(*) AS anzahl
                    FROM spieler
                    GROUP BY klasse;

                    klasse   | anzahl
                    ---------+-------
                    Krieger  |      5
                    Magier   |      5
                    ...

                GROUP BY packt alle Zeilen mit gleichem Wert in einen "Eimer". Die Aggregatfunktion
                rechnet dann PRO EIMER.

                # ⚠ Die goldene Regel
                Jede Spalte im SELECT muss entweder
                * in GROUP BY stehen, oder
                * in einer Aggregatfunktion stecken.
                    SELECT klasse, spieler_name, COUNT(*) FROM spieler GROUP BY klasse;   -- FALSCH!
                Welcher spieler_name soll denn für "Krieger" angezeigt werden? Es sind 5!
                ! MySQL meldet hier Fehler 1055 (ONLY_FULL_GROUP_BY). SQLite nimmt leider einfach irgendeinen.
                ---
                # Mehrere Gruppierungsspalten
                    SELECT typ, seltenheit, COUNT(*) FROM gegenstaende GROUP BY typ, seltenheit;
                → ein Eimer pro KOMBINATION.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Wie viele Spieler hat jede Klasse? Spalten: klasse, `anzahl`.",
                    "loesung": "SELECT klasse, COUNT(*) AS anzahl FROM spieler GROUP BY klasse;",
                    "spalten": True,
                },
                {
                    "aufgabe": "Zeige pro Gegenstands-typ: typ, durchschnittlichen Wert gerundet auf 2 Stellen (`schnitt`) und Anzahl (`anzahl`).",
                    "loesung": "SELECT typ, ROUND(AVG(wert), 2) AS schnitt, COUNT(*) AS anzahl FROM gegenstaende GROUP BY typ;",
                    "spalten": True,
                },
                {
                    "aufgabe": "Zeige pro seltenheit die Summe der Werte (`gesamtwert`), sortiert nach gesamtwert absteigend.",
                    "loesung": "SELECT seltenheit, SUM(wert) AS gesamtwert FROM gegenstaende GROUP BY seltenheit ORDER BY gesamtwert DESC;",
                    "spalten": True,
                },
                {
                    "aufgabe": "Zeige pro Gebiet: gebiet, Anzahl Monster (`anzahl`) und die höchste Stufe (`max_stufe`). Sortiert nach gebiet.",
                    "loesung": "SELECT gebiet, COUNT(*) AS anzahl, MAX(stufe) AS max_stufe FROM monster GROUP BY gebiet ORDER BY gebiet;",
                    "spalten": True,
                },
                {
                    "aufgabe": "Zähle die Gegenstände pro Kombination aus typ und seltenheit (Spalten: typ, seltenheit, `anzahl`), sortiert nach typ und seltenheit.",
                    "loesung": "SELECT typ, seltenheit, COUNT(*) AS anzahl FROM gegenstaende GROUP BY typ, seltenheit ORDER BY typ, seltenheit;",
                    "spalten": True,
                },
                {
                    "aufgabe": "Wie viele Spieler wurden pro Jahr erstellt? Spalten `jahr` und `anzahl`, chronologisch.",
                    "loesung": "SELECT YEAR(erstellt_am) AS jahr, COUNT(*) AS anzahl FROM spieler GROUP BY YEAR(erstellt_am) ORDER BY jahr;",
                    "auch_richtig": ["SELECT YEAR(erstellt_am) AS jahr, COUNT(*) AS anzahl FROM spieler GROUP BY jahr ORDER BY jahr;"],
                    "spalten": True,
                },
            ],
        },
        {
            "titel": "HAVING & die Ausführungsreihenfolge",
            "theorie": """
                # WHERE filtert ZEILEN, HAVING filtert GRUPPEN
                    SELECT klasse, COUNT(*) AS anzahl
                    FROM spieler
                    GROUP BY klasse
                    HAVING COUNT(*) > 3;

                `WHERE COUNT(*) > 3` geht NICHT – beim WHERE gibt es noch keine Gruppen!
                ---
                # In welcher Reihenfolge arbeitet die Datenbank? (Prüfungsfrage!)
                    Schreibreihenfolge       Ausführungsreihenfolge
                    1 SELECT                 1 FROM       – Tabellen holen (und JOINs)
                    2 FROM                   2 WHERE      – Zeilen filtern
                    3 WHERE                  3 GROUP BY   – gruppieren
                    4 GROUP BY               4 HAVING     – Gruppen filtern
                    5 HAVING                 5 SELECT     – Spalten berechnen, Aliase vergeben
                    6 ORDER BY               6 ORDER BY   – sortieren
                    7 LIMIT                  7 LIMIT      – abschneiden

                Daraus folgt:
                * Im WHERE kann man noch keine SELECT-Aliase benutzen (gibt es noch nicht).
                * Im ORDER BY schon.
                ! MySQL (und SQLite) erlauben Aliase im HAVING/GROUP BY als Bonus – Standard-SQL nicht.
                ? Eselsbrücke: "Fiese Wichtel Gruppieren Heimlich Seltene Ostereier Leise"
                ? Live ansehen: Schreib eine Abfrage und klick auf 🔍 Ablauf (Terminal: .a SELECT ...).
                ? Du siehst jeden dieser Schritte mit seinem Zwischenergebnis – welche Zeilen WHERE rauswirft,
                ? welche Gruppen GROUP BY bildet, was HAVING übrig lässt.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Welche Klassen haben mehr als 3 Spieler? Spalten: klasse, `anzahl`.",
                    "loesung": "SELECT klasse, COUNT(*) AS anzahl FROM spieler GROUP BY klasse HAVING COUNT(*) > 3;",
                    "spalten": True,
                    "muss_enthalten": ["HAVING"],
                },
                {
                    "aufgabe": "Welche Gebiete haben mehr als ein Monster? Zeige gebiet und `anzahl`.",
                    "loesung": "SELECT gebiet, COUNT(*) AS anzahl FROM monster GROUP BY gebiet HAVING COUNT(*) > 1;",
                    "spalten": True,
                },
                {
                    "aufgabe": """
                        Berücksichtige nur Gegenstände mit einem Wert über 50. Zeige pro typ die Anzahl (`anzahl`) und den
                        Durchschnittswert (`schnitt`) – aber nur Typen mit mindestens 2 solchen Gegenständen.
                        Sortiert nach schnitt absteigend.
                    """,
                    "loesung": """SELECT typ, COUNT(*) AS anzahl, AVG(wert) AS schnitt FROM gegenstaende
                        WHERE wert > 50 GROUP BY typ HAVING COUNT(*) >= 2 ORDER BY schnitt DESC;""",
                    "spalten": True,
                    "hinweise": ["WHERE wert > 50 kommt VOR GROUP BY, HAVING COUNT(*) >= 2 danach."],
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Welche Klausel wird bei der Ausführung ZUERST abgearbeitet?",
                    "optionen": ["SELECT", "WHERE", "FROM", "GROUP BY"],
                    "richtig": 3,
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Warum funktioniert `SELECT name, wert * 2 AS doppelt FROM gegenstaende WHERE doppelt > 1000;` in Standard-SQL nicht?",
                    "optionen": ["Weil man nicht multiplizieren darf",
                                 "Weil WHERE vor SELECT ausgeführt wird – den Alias gibt es da noch nicht",
                                 "Weil AS nur bei Tabellen geht",
                                 "Es funktioniert problemlos"],
                    "richtig": 2,
                    "erklaerung": "Lösung: WHERE wert * 2 > 1000. (SQLite ist hier nachsichtig, MySQL nicht.)",
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Du willst nur Gilden-IDs, deren Mitglieder im Schnitt über Level 12 sind. Wo steht die Bedingung AVG(level) > 12?",
                    "optionen": ["im WHERE", "im HAVING", "im ORDER BY", "im FROM"],
                    "richtig": 2,
                },
            ],
        },
        {
            "titel": "GROUP_CONCAT, bedingte Aggregation, Fensterfunktionen",
            "theorie": """
                # GROUP_CONCAT – Werte einer Gruppe als Text
                    SELECT klasse, GROUP_CONCAT(spieler_name ORDER BY spieler_name SEPARATOR ', ')
                    FROM spieler GROUP BY klasse;
                → Krieger | BerserkerBob, GhostRider, IronWall, ...
                ! Das ist MySQL-Schreibweise (wird hier übersetzt). SQLite: GROUP_CONCAT(x, ', ' ORDER BY x).
                ! PostgreSQL: STRING_AGG(x, ', ').
                ---
                # Bedingte Aggregation – Pivot in einer Zeile
                    SELECT
                        SUM(CASE WHEN klasse = 'Krieger' THEN 1 ELSE 0 END) AS krieger,
                        SUM(CASE WHEN klasse = 'Magier'  THEN 1 ELSE 0 END) AS magier
                    FROM spieler;
                CASE macht aus jeder Zeile 1 oder 0, SUM zählt die Einsen.
                ---
                # Fensterfunktionen (Window Functions) – Bonus, aber sehr praxisrelevant
                Aggregieren, OHNE die Zeilen zusammenzufassen:
                    SELECT spieler_name, klasse, level,
                           RANK() OVER (PARTITION BY klasse ORDER BY level DESC) AS platz,
                           AVG(level) OVER (PARTITION BY klasse) AS klassen_schnitt
                    FROM spieler;

                * `PARTITION BY` = wie GROUP BY, aber jede Zeile bleibt erhalten.
                * `ROW_NUMBER()` 1,2,3,4 · `RANK()` 1,2,2,4 · `DENSE_RANK()` 1,2,2,3
                * `SUM(x) OVER (ORDER BY datum)` = laufende Summe.
                ! Fensterfunktionen gibt es in MySQL ab Version 8.0.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige pro Klasse alle Spielernamen, alphabetisch sortiert und mit ', ' getrennt, als `spieler`. Sortiere nach klasse.",
                    "loesung": "SELECT klasse, GROUP_CONCAT(spieler_name ORDER BY spieler_name SEPARATOR ', ') AS spieler FROM spieler GROUP BY klasse ORDER BY klasse;",
                    "auch_richtig": ["SELECT klasse, GROUP_CONCAT(spieler_name, ', ' ORDER BY spieler_name) AS spieler FROM spieler GROUP BY klasse ORDER BY klasse;"],
                    "spalten": True,
                    "hinweise": ["GROUP_CONCAT(spieler_name ORDER BY spieler_name SEPARATOR ', ')"],
                },
                {
                    "aufgabe": "Zähle in EINER Zeile die Spieler pro Klasse als Spalten `krieger`, `magier`, `schurken`, `priester`.",
                    "loesung": """SELECT SUM(CASE WHEN klasse = 'Krieger' THEN 1 ELSE 0 END) AS krieger,
                        SUM(CASE WHEN klasse = 'Magier' THEN 1 ELSE 0 END) AS magier,
                        SUM(CASE WHEN klasse = 'Schurke' THEN 1 ELSE 0 END) AS schurken,
                        SUM(CASE WHEN klasse = 'Priester' THEN 1 ELSE 0 END) AS priester FROM spieler;""",
                    "spalten": True,
                    "hinweise": ["SUM(CASE WHEN klasse = 'Krieger' THEN 1 ELSE 0 END) AS krieger, ..."],
                },
                {
                    "aufgabe": """
                        Zeige spieler_name, klasse, level und `platz` = Rang des Spielers INNERHALB seiner Klasse
                        nach Level (höchstes Level = Platz 1, RANK). Sortiert nach klasse, platz.
                    """,
                    "loesung": """SELECT spieler_name, klasse, level, RANK() OVER (PARTITION BY klasse ORDER BY level DESC) AS platz
                        FROM spieler ORDER BY klasse, platz;""",
                    "spalten": True,
                    "hinweise": ["RANK() OVER (PARTITION BY klasse ORDER BY level DESC) AS platz"],
                },
                {
                    "aufgabe": "Zeige name, stufe und die laufende Summe der Stufen (`summe_bisher`) aller Monster, sortiert nach monster_id.",
                    "loesung": "SELECT name, stufe, SUM(stufe) OVER (ORDER BY monster_id) AS summe_bisher FROM monster ORDER BY monster_id;",
                    "spalten": True,
                    "hinweise": ["SUM(stufe) OVER (ORDER BY monster_id)"],
                },
            ],
        },
    ],
    "boss": {
        "titel": "Der Statistiker von Malakor",
        "story": """
            # Malakors Statistiker will wissen, wo die gefährlichsten Gebiete sind.
        """,
        "aufgabe": """
            Zeige pro Gebiet:
              gebiet, `anzahl` Monster, `schnitt_stufe` (Durchschnitt, auf 1 Stelle gerundet),
              `boss_anzahl` (wie viele Bosse dort leben)
            Nur Gebiete, deren Durchschnittsstufe mindestens 5 ist.
            Sortiert nach schnitt_stufe absteigend, bei Gleichstand nach gebiet.
        """,
        "loesung": """SELECT gebiet, COUNT(*) AS anzahl, ROUND(AVG(stufe), 1) AS schnitt_stufe, SUM(ist_boss) AS boss_anzahl
            FROM monster
            GROUP BY gebiet
            HAVING AVG(stufe) >= 5
            ORDER BY schnitt_stufe DESC, gebiet;""",
        "auch_richtig": ["""SELECT gebiet, COUNT(*) AS anzahl, ROUND(AVG(stufe), 1) AS schnitt_stufe,
            SUM(CASE WHEN ist_boss = 1 THEN 1 ELSE 0 END) AS boss_anzahl FROM monster
            GROUP BY gebiet HAVING AVG(stufe) >= 5 ORDER BY schnitt_stufe DESC, gebiet;"""],
        "spalten": True,
        "hinweise": ["boss_anzahl: SUM(ist_boss) – oder SUM(CASE WHEN ist_boss = 1 THEN 1 ELSE 0 END)",
                     "HAVING AVG(stufe) >= 5"],
    },
}
