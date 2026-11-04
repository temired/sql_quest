KAPITEL = {
    "nr": 5,
    "titel": "Basic Queries",
    "lektionen": [
        {
            "titel": "SELECT, Aliase & Rechnen",
            "theorie": """
                # Spalten auswählen
                    SELECT * FROM spieler;                       -- alle Spalten
                    SELECT spieler_name, level FROM spieler;     -- nur diese
                ? In echten Programmen `SELECT *` vermeiden: Man holt unnötige Daten und
                ? der Code bricht, wenn sich die Tabelle ändert.

                # Aliase mit AS – Spalten umbenennen (nur in der Ausgabe)
                    SELECT spieler_name AS Spieler, level AS Stufe FROM spieler;
                * Alias mit Leerzeichen/Umlauten: in Anführungszeichen `AS "Aktuelle Stufe"`
                  (MySQL: auch mit Backticks `Aktuelle Stufe`).
                * `AS` darf man weglassen (`spieler_name Spieler`) – lesbarer ist es mit.
                ---
                # Berechnete Spalten
                    SELECT spieler_name, level, 100 - level AS fehlende_level FROM spieler;
                    SELECT name, wert, wert * 0.75 AS verkaufspreis FROM gegenstaende;

                Operatoren: `+  -  *  /` und `%` (Rest/Modulo).

                # ⚠ Die Ganzzahl-Falle
                    SELECT 7 / 2;      -- SQLite: 3        MySQL: 3.5000
                    SELECT 7 / 2.0;    -- überall: 3.5
                ! MySQL hat für Ganzzahldivision extra `DIV`: `7 DIV 2` = 3.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige spieler_name und level aller Spieler – aber die Spalten sollen `Spieler` und `Stufe` heißen.",
                    "loesung": "SELECT spieler_name AS Spieler, level AS Stufe FROM spieler;",
                    "spalten": True,
                    "hinweise": ["spieler_name AS Spieler"],
                },
                {
                    "aufgabe": "Zeige name, wert und den Verkaufspreis (75 % vom Wert) aller Gegenstände. Die neue Spalte heißt `verkaufspreis`.",
                    "loesung": "SELECT name, wert, wert * 0.75 AS verkaufspreis FROM gegenstaende;",
                    "spalten": True,
                    "hinweise": ["wert * 0.75 AS verkaufspreis"],
                },
                {
                    "aufgabe": "Zeige name, stufe und die Erfahrungspunkte für das Besiegen jedes Monsters: stufe * stufe * 10 als `xp`.",
                    "loesung": "SELECT name, stufe, stufe * stufe * 10 AS xp FROM monster;",
                    "spalten": True,
                    "hinweise": ["stufe * stufe * 10 AS xp"],
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Welchen Wert liefert `SELECT 9 / 2;` in SQLite (und in MySQL mit `9 DIV 2`)?",
                    "optionen": ["4.5", "4", "5", "Fehler"],
                    "richtig": 2,
                    "erklaerung": "Ganzzahl / Ganzzahl = Ganzzahl (abgeschnitten). Für 4.5 schreibt man 9 / 2.0.",
                },
            ],
        },
        {
            "titel": "DISTINCT",
            "theorie": """
                # Duplikate entfernen
                    SELECT klasse FROM spieler;            -- 18 Zeilen, viele doppelt
                    SELECT DISTINCT klasse FROM spieler;   -- 4 Zeilen: jede Klasse einmal

                DISTINCT gilt für die ganze ZEILE, also für alle Spalten zusammen:
                    SELECT DISTINCT typ, seltenheit FROM gegenstaende;
                → jede KOMBINATION aus typ und seltenheit einmal.
                ? DISTINCT steht direkt hinter SELECT, nicht vor einer einzelnen Spalte.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Welche Klassen gibt es? Zeige jede Klasse nur einmal.",
                    "loesung": "SELECT DISTINCT klasse FROM spieler;",
                    "hinweise": ["SELECT DISTINCT ..."],
                },
                {
                    "aufgabe": "In welchen Gebieten gibt es Monster? Jedes Gebiet nur einmal.",
                    "loesung": "SELECT DISTINCT gebiet FROM monster;",
                },
                {
                    "aufgabe": "Zeige alle vorkommenden Kombinationen aus typ und seltenheit der Gegenstände (jede nur einmal).",
                    "loesung": "SELECT DISTINCT typ, seltenheit FROM gegenstaende;",
                    "hinweise": ["DISTINCT wirkt auf alle Spalten gemeinsam."],
                },
            ],
        },
        {
            "titel": "WHERE & Logik",
            "theorie": """
                # WHERE – Zeilen filtern
                    SELECT spieler_name, level FROM spieler WHERE level > 10;

                    Operator  | Bedeutung
                    ----------+------------------
                    =         | gleich
                    <> oder !=| ungleich
                    < >       | kleiner / größer
                    <= >=     | kleiner-gleich / größer-gleich

                * Texte in '...': `WHERE klasse = 'Magier'`
                * Datum ist auch Text im Format JJJJ-MM-TT und lässt sich vergleichen: `WHERE erstellt_am >= '2024-01-01'`
                ---
                # AND, OR, NOT
                    WHERE klasse = 'Magier' AND level >= 12     -- beide Bedingungen
                    WHERE klasse = 'Priester' OR klasse = 'Schurke'  -- mindestens eine
                    WHERE NOT klasse = 'Krieger'                 -- Umkehrung

                # ⚠ Vorrang: AND bindet stärker als OR!
                    WHERE klasse = 'Krieger' OR klasse = 'Schurke' AND level > 10
                wird gelesen als
                    WHERE klasse = 'Krieger' OR (klasse = 'Schurke' AND level > 10)
                → ALLE Krieger, auch Level 3! Richtig mit Klammern:
                    WHERE (klasse = 'Krieger' OR klasse = 'Schurke') AND level > 10
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige spieler_name und klasse aller Magier.",
                    "loesung": "SELECT spieler_name, klasse FROM spieler WHERE klasse = 'Magier';",
                    "hinweise": ["WHERE klasse = 'Magier'"],
                },
                {
                    "aufgabe": "Zeige spieler_name und level aller Spieler über Level 10 (also ab 11).",
                    "loesung": "SELECT spieler_name, level FROM spieler WHERE level > 10;",
                },
                {
                    "aufgabe": "Zeige spieler_name und klasse aller Spieler, die KEINE Krieger sind.",
                    "loesung": "SELECT spieler_name, klasse FROM spieler WHERE klasse <> 'Krieger';",
                    "hinweise": ["<> oder != bedeutet ungleich."],
                },
                {
                    "aufgabe": "Zeige spieler_name, klasse, level aller Magier ab Level 12.",
                    "loesung": "SELECT spieler_name, klasse, level FROM spieler WHERE klasse = 'Magier' AND level >= 12;",
                },
                {
                    "aufgabe": "Zeige spieler_name, klasse, level aller Krieger UND Schurken, die über Level 10 sind. (Achtung, Klammern!)",
                    "loesung": "SELECT spieler_name, klasse, level FROM spieler WHERE (klasse = 'Krieger' OR klasse = 'Schurke') AND level > 10;",
                    "falsch": ["SELECT spieler_name, klasse, level FROM spieler WHERE klasse = 'Krieger' OR klasse = 'Schurke' AND level > 10;"],
                    "hinweise": ["(klasse = ... OR klasse = ...) AND level > 10"],
                },
                {
                    "aufgabe": "Zeige spieler_name und erstellt_am aller Spieler, die im Jahr 2024 oder später erstellt wurden.",
                    "loesung": "SELECT spieler_name, erstellt_am FROM spieler WHERE erstellt_am >= '2024-01-01';",
                    "hinweise": ["Datumswerte vergleicht man wie Texte: >= '2024-01-01'"],
                },
            ],
        },
        {
            "titel": "BETWEEN, IN, LIKE",
            "theorie": """
                # BETWEEN – Bereich (Grenzen INKLUSIVE)
                    WHERE stufe BETWEEN 5 AND 10       -- = stufe >= 5 AND stufe <= 10
                    WHERE erstellt_am BETWEEN '2023-01-01' AND '2023-12-31'

                # IN – Liste von Werten
                    WHERE seltenheit IN ('Episch', 'Legendär')     -- statt vieler ORs
                    WHERE typ NOT IN ('Trank', 'Nahrung')
                ---
                # LIKE – Textmuster
                    Platzhalter | Bedeutung
                    ------------+------------------------------
                    %           | beliebig viele Zeichen (auch 0)
                    _           | genau EIN Zeichen

                    WHERE name LIKE 'Feuer%'      -- beginnt mit Feuer
                    WHERE name LIKE '%klinge'     -- endet auf klinge
                    WHERE titel LIKE '%Sumpf%'    -- enthält Sumpf
                    WHERE klasse LIKE '____'      -- genau 4 Zeichen
                    WHERE name NOT LIKE '%spinne'

                ! In MySQL ist LIKE meist NICHT case-sensitiv ('feuer%' findet 'Feuermantel').
                ! In SQLite gilt das nur für ASCII-Buchstaben – Umlaute schon (ä ≠ Ä).
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige name, gebiet, stufe aller Monster mit einer Stufe von 5 bis 10 (einschließlich). Benutze BETWEEN.",
                    "loesung": "SELECT name, gebiet, stufe FROM monster WHERE stufe BETWEEN 5 AND 10;",
                    "muss_enthalten": ["BETWEEN"],
                },
                {
                    "aufgabe": "Zeige name, seltenheit, wert aller Gegenstände, die 'Episch' oder 'Legendär' sind. Benutze IN.",
                    "loesung": "SELECT name, seltenheit, wert FROM gegenstaende WHERE seltenheit IN ('Episch', 'Legendär');",
                    "muss_enthalten": ["IN"],
                },
                {
                    "aufgabe": "Zeige name und typ aller Gegenstände, die weder 'Trank' noch 'Nahrung' sind (NOT IN).",
                    "loesung": "SELECT name, typ FROM gegenstaende WHERE typ NOT IN ('Trank', 'Nahrung');",
                },
                {
                    "aufgabe": "Zeige name und wert aller Gegenstände, deren Name auf 'klinge' endet.",
                    "loesung": "SELECT name, wert FROM gegenstaende WHERE name LIKE '%klinge';",
                    "hinweise": ["% = beliebig viele Zeichen davor"],
                },
                {
                    "aufgabe": "Zeige alle spieler_name, die mit 'Shadow' beginnen.",
                    "loesung": "SELECT spieler_name FROM spieler WHERE spieler_name LIKE 'Shadow%';",
                },
                {
                    "aufgabe": "Zeige name und gebiet aller Monster, deren Gebiet 'wald' enthält, deren Name aber NICHT auf 'spinne' endet.",
                    "loesung": "SELECT name, gebiet FROM monster WHERE gebiet LIKE '%wald%' AND name NOT LIKE '%spinne';",
                },
                {
                    "aufgabe": "Zeige alle spieler_name, die aus genau 8 Zeichen bestehen (mit _).",
                    "loesung": "SELECT spieler_name FROM spieler WHERE spieler_name LIKE '________';",
                    "hinweise": ["8 Unterstriche: '________'"],
                },
            ],
        },
        {
            "titel": "NULL – der Wert, der keiner ist",
            "theorie": """
                # NULL = unbekannt / nicht vorhanden
                NULL ist NICHT 0 und NICHT '' (leerer Text). Es heißt: "Wir wissen es nicht."
                Darum ergibt JEDER Vergleich mit NULL wieder NULL (= unbekannt) – nie wahr:

                    NULL = NULL     → NULL  (nicht TRUE!)
                    NULL <> 5       → NULL
                    NULL + 10       → NULL

                Deshalb findet `WHERE gilde_id = NULL` NICHTS. Richtig:
                    WHERE gilde_id IS NULL
                    WHERE gilde_id IS NOT NULL
                ---
                # Dreiwertige Logik
                SQL kennt TRUE, FALSE und UNKNOWN (NULL). WHERE behält nur Zeilen mit TRUE.

                    AND     | TRUE    FALSE   NULL         OR      | TRUE   FALSE   NULL
                    TRUE    | TRUE    FALSE   NULL         TRUE    | TRUE   TRUE    TRUE
                    FALSE   | FALSE   FALSE   FALSE        FALSE   | TRUE   FALSE   NULL
                    NULL    | NULL    FALSE   NULL         NULL    | TRUE   NULL    NULL

                ⚠ Falle: `WHERE gilde_id <> 1` liefert die Spieler OHNE Gilde NICHT mit!
                (NULL <> 1 ist NULL, nicht TRUE.)
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige spieler_name aller Spieler, die in KEINER Gilde sind.",
                    "loesung": "SELECT spieler_name FROM spieler WHERE gilde_id IS NULL;",
                    "hinweise": ["IS NULL – nicht = NULL"],
                },
                {
                    "aufgabe": "Zeige titel und belohnung_gold aller Quests, die ein Zielmonster haben.",
                    "loesung": "SELECT titel, belohnung_gold FROM quests WHERE ziel_monster_id IS NOT NULL;",
                },
                {
                    "aufgabe": "Zeige spieler_name und gilde_id aller Spieler, die NICHT in Gilde 1 sind – die gildenlosen Spieler sollen auch dabei sein!",
                    "loesung": "SELECT spieler_name, gilde_id FROM spieler WHERE gilde_id <> 1 OR gilde_id IS NULL;",
                    "falsch": ["SELECT spieler_name, gilde_id FROM spieler WHERE gilde_id <> 1;"],
                    "hinweise": ["gilde_id <> 1 allein verliert die NULL-Zeilen.", "... OR gilde_id IS NULL"],
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Wie viele Zeilen liefert `SELECT * FROM spieler WHERE gilde_id = NULL;`?",
                    "optionen": ["3 (die Spieler ohne Gilde)", "0", "Alle 18", "Fehler"],
                    "richtig": 2,
                    "erklaerung": "gilde_id = NULL ist nie TRUE, sondern immer UNKNOWN → 0 Zeilen. Kein Fehler, aber falsch!",
                },
            ],
        },
    ],
    "boss": {
        "titel": "Das Orakel der Händler",
        "story": """
            # Das Orakel sucht Ausrüstung für eine Expedition.
            "Bring mir eine Liste – aber genau so, wie ich sie will!"
        """,
        "aufgabe": """
            Zeige von allen Gegenständen, die
              • Waffe ODER Rüstung sind,
              • einen Wert von 300 bis 1500 haben (inklusive),
              • und deren Name NICHT 'schild' enthält,
            die Spalten: `name`, `typ`, `wert` und `ankaufspreis` (= Wert * 0.6).
        """,
        "loesung": """SELECT name, typ, wert, wert * 0.6 AS ankaufspreis
            FROM gegenstaende
            WHERE typ IN ('Waffe', 'Rüstung')
              AND wert BETWEEN 300 AND 1500
              AND name NOT LIKE '%schild%';""",
        "spalten": True,
        "falsch": ["SELECT name, typ, wert, wert * 0.6 AS ankaufspreis FROM gegenstaende WHERE typ = 'Waffe' OR typ = 'Rüstung' AND wert BETWEEN 300 AND 1500 AND name NOT LIKE '%schild%';"],
        "hinweise": ["typ IN ('Waffe', 'Rüstung')", "Bei OR an Klammern denken!"],
    },
}
