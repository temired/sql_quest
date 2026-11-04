from ._hilfe import VIEWS

KAPITEL = {
    "nr": 6,
    "titel": "Structuring",
    "lektionen": [
        {
            "titel": "ORDER BY – Sortieren",
            "theorie": """
                # Ohne ORDER BY gibt es KEINE garantierte Reihenfolge!
                    SELECT spieler_name, level FROM spieler ORDER BY level;        -- aufsteigend (ASC, Standard)
                    SELECT spieler_name, level FROM spieler ORDER BY level DESC;   -- absteigend

                # Mehrere Sortierkriterien
                    ORDER BY klasse ASC, level DESC
                → erst nach Klasse; innerhalb derselben Klasse nach Level absteigend.
                Das zweite Kriterium greift nur bei Gleichstand im ersten ("Tie-Breaker").

                # Sortieren nach Alias oder Spaltennummer
                    SELECT name, wert * 0.75 AS vk FROM gegenstaende ORDER BY vk DESC;
                    SELECT name, wert FROM gegenstaende ORDER BY 2 DESC;  -- 2. Spalte (unschön, aber erlaubt)

                ? NULL gilt in MySQL und SQLite beim Sortieren als kleinster Wert (bei ASC zuerst).
                ? Texte sortieren alphabetisch, Datumswerte (JJJJ-MM-TT) chronologisch.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige spieler_name und level, sortiert nach level absteigend. Bei gleichem Level alphabetisch nach Name.",
                    "loesung": "SELECT spieler_name, level FROM spieler ORDER BY level DESC, spieler_name ASC;",
                    "hinweise": ["ORDER BY level DESC, spieler_name"],
                },
                {
                    "aufgabe": "Zeige name, typ, wert aller Gegenstände – der teuerste zuerst.",
                    "loesung": "SELECT name, typ, wert FROM gegenstaende ORDER BY wert DESC;",
                },
                {
                    "aufgabe": "Zeige spieler_name, klasse, level – sortiert nach Klasse (A–Z) und innerhalb der Klasse nach Level (höchstes zuerst).",
                    "loesung": "SELECT spieler_name, klasse, level FROM spieler ORDER BY klasse ASC, level DESC;",
                },
                {
                    "aufgabe": "Zeige spieler_name und erstellt_am aller Spieler – der älteste Account zuerst.",
                    "loesung": "SELECT spieler_name, erstellt_am FROM spieler ORDER BY erstellt_am;",
                },
            ],
        },
        {
            "titel": "LIMIT & OFFSET",
            "theorie": """
                # Nur die ersten N Zeilen
                    SELECT spieler_name, level FROM spieler ORDER BY level DESC LIMIT 3;  -- Top 3

                # Seitenweise blättern (Paging)
                    LIMIT 5 OFFSET 0     -- Seite 1: Zeilen 1-5
                    LIMIT 5 OFFSET 5     -- Seite 2: Zeilen 6-10
                    LIMIT 5 OFFSET 10    -- Seite 3: Zeilen 11-15
                Formel: OFFSET = (seite - 1) * zeilen_pro_seite

                ! MySQL-Kurzform: `LIMIT 10, 5` = OFFSET 10, 5 Zeilen (erst Offset, dann Anzahl!) – geht auch hier.
                ! MS SQL Server nutzt stattdessen `SELECT TOP 3 ...`, Oracle `FETCH FIRST 3 ROWS ONLY`.

                ? LIMIT ohne ORDER BY ergibt "irgendwelche" Zeilen – fast immer ein Fehler.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige die 3 Spieler mit dem höchsten Level (spieler_name, level).",
                    "loesung": "SELECT spieler_name, level FROM spieler ORDER BY level DESC LIMIT 3;",
                },
                {
                    "aufgabe": "Zeige die 3 billigsten Gegenstände (name, wert). Gegenstände ohne Wert (NULL) sollen nicht vorkommen.",
                    "loesung": "SELECT name, wert FROM gegenstaende WHERE wert IS NOT NULL ORDER BY wert ASC LIMIT 3;",
                    "hinweise": ["NULL wäre sonst der 'kleinste' Wert: WHERE wert IS NOT NULL"],
                },
                {
                    "aufgabe": "Monster-Bestiarium, 5 Monster pro Seite, sortiert nach stufe und bei Gleichstand nach name. Zeige SEITE 2 (name, stufe).",
                    "loesung": "SELECT name, stufe FROM monster ORDER BY stufe, name LIMIT 5 OFFSET 5;",
                    "auch_richtig": ["SELECT name, stufe FROM monster ORDER BY stufe, name LIMIT 5, 5;"],
                    "hinweise": ["Seite 2 → OFFSET 5"],
                },
            ],
        },
        {
            "titel": "CASE WHEN – Fallunterscheidung",
            "theorie": """
                # Das IF von SQL
                    SELECT spieler_name, level,
                        CASE
                            WHEN level < 10 THEN 'Anfänger'
                            WHEN level <= 15 THEN 'Fortgeschritten'
                            ELSE 'Veteran'
                        END AS rang
                    FROM spieler;

                * Die WHEN-Zweige werden von oben nach unten geprüft – der ERSTE passende gewinnt.
                * Ohne ELSE gibt es NULL, wenn nichts passt.
                * Immer mit `END` abschließen (und am besten einen Alias vergeben).

                # Kurzform: einfacher Vergleich auf einen Wert
                    CASE ist_boss WHEN 1 THEN 'Boss' ELSE 'Normal' END

                ! MySQL hat außerdem `IF(bedingung, dann, sonst)`: `IF(ist_boss = 1, 'Boss', 'Normal')` – geht hier auch.
                ? CASE geht überall: im SELECT, im ORDER BY, im UPDATE ... SET, in Aggregaten (Kapitel 7).
            """,
            "aufgaben": [
                {
                    "aufgabe": """
                        Zeige spieler_name, level und eine Spalte `rang`:
                          level unter 10 → 'Anfänger', level 10 bis 15 → 'Fortgeschritten', sonst 'Veteran'
                    """,
                    "loesung": """SELECT spieler_name, level,
                        CASE WHEN level < 10 THEN 'Anfänger' WHEN level <= 15 THEN 'Fortgeschritten' ELSE 'Veteran' END AS rang
                        FROM spieler;""",
                    "spalten": True,
                    "hinweise": ["CASE WHEN ... THEN ... WHEN ... THEN ... ELSE ... END AS rang"],
                },
                {
                    "aufgabe": "Zeige name und eine Spalte `art` für alle Monster: 'Boss', wenn ist_boss 1 ist, sonst 'Normal'.",
                    "loesung": "SELECT name, CASE ist_boss WHEN 1 THEN 'Boss' ELSE 'Normal' END AS art FROM monster;",
                    "spalten": True,
                },
                {
                    "aufgabe": """
                        Sortiere die Gegenstände nach Seltenheit in der Reihenfolge Legendär, Episch, Selten, Gewöhnlich
                        (innerhalb gleicher Seltenheit nach name). Zeige name und seltenheit.
                        (Tipp: CASE im ORDER BY, das jeder Seltenheit eine Zahl gibt.)
                    """,
                    "loesung": """SELECT name, seltenheit FROM gegenstaende
                        ORDER BY CASE seltenheit WHEN 'Legendär' THEN 1 WHEN 'Episch' THEN 2 WHEN 'Selten' THEN 3 ELSE 4 END, name;""",
                    "hinweise": ["ORDER BY CASE seltenheit WHEN 'Legendär' THEN 1 WHEN ... END, name"],
                },
            ],
        },
        {
            "titel": "Text-Funktionen",
            "theorie": """
                # Texte bearbeiten
                    Funktion                      | Ergebnis
                    ------------------------------+------------------------------
                    UPPER('Magier')               | MAGIER
                    LOWER('Magier')               | magier
                    LENGTH('Magier')              | 6   (MySQL: Bytes! CHAR_LENGTH für Zeichen)
                    SUBSTR('Flammenschwert', 1, 6)| Flamme   (Start bei 1, Länge 6)
                    LEFT('Flammenschwert', 3)     | Fla
                    RIGHT('Flammenschwert', 7)    | schwert  (die letzten 7)
                    REPLACE('Heiltrank','trank','salbe') | Heilsalbe
                    TRIM('  Hallo  ')             | Hallo
                    CONCAT('Fire', 'Mage')        | FireMage
                    'Fire' || 'Mage'              | FireMage (Standard-SQL / SQLite)

                ! In MySQL ist `||` standardmäßig ein logisches ODER! Dort IMMER `CONCAT()` benutzen.
                ! `CONCAT_WS(', ', a, b, c)` fügt mit Trennzeichen zusammen.
                ? CONCAT mit einem NULL-Wert ergibt in MySQL NULL.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige alle Spielernamen in GROSSBUCHSTABEN, Spaltenname `name_gross`.",
                    "loesung": "SELECT UPPER(spieler_name) AS name_gross FROM spieler;",
                    "spalten": True,
                },
                {
                    "aufgabe": "Zeige spieler_name und die Länge des Namens als `laenge` – der längste Name zuerst, bei Gleichstand alphabetisch.",
                    "loesung": "SELECT spieler_name, LENGTH(spieler_name) AS laenge FROM spieler ORDER BY laenge DESC, spieler_name;",
                    "spalten": True,
                },
                {
                    "aufgabe": "Erzeuge für jeden Spieler die Spalte `anzeige` im Format: ShadowKnight (Krieger, Lvl 12)",
                    "loesung": "SELECT CONCAT(spieler_name, ' (', klasse, ', Lvl ', level, ')') AS anzeige FROM spieler;",
                    "auch_richtig": ["SELECT spieler_name || ' (' || klasse || ', Lvl ' || level || ')' AS anzeige FROM spieler;"],
                    "spalten": True,
                    "hinweise": ["CONCAT(spieler_name, ' (', klasse, ', Lvl ', level, ')')"],
                },
                {
                    "aufgabe": "Zeige name und die ersten 3 Buchstaben des Namens als `kuerzel` für alle Monster.",
                    "loesung": "SELECT name, SUBSTR(name, 1, 3) AS kuerzel FROM monster;",
                    "auch_richtig": ["SELECT name, LEFT(name, 3) AS kuerzel FROM monster;"],
                    "spalten": True,
                },
                {
                    "aufgabe": "Zeige die Quest-Titel, wobei 'Sumpf' durch 'Moor' ersetzt wird (Spalte `neuer_titel`). Nur Quests, deren Titel 'Sumpf' enthält.",
                    "loesung": "SELECT REPLACE(titel, 'Sumpf', 'Moor') AS neuer_titel FROM quests WHERE titel LIKE '%Sumpf%';",
                    "spalten": True,
                },
            ],
        },
        {
            "titel": "Zahlen, Datum, NULL-Funktionen, CAST",
            "theorie": """
                # Zahlen
                    ROUND(3.14159, 2)  → 3.14       ROUND(2.5) → 3
                    ABS(-7)            → 7
                    17 % 5             → 2   (Rest, MySQL auch MOD(17,5))
                ! MySQL: CEIL(2.1) → 3, FLOOR(2.9) → 2, TRUNCATE(2.99, 1) → 2.9
                ---
                # Datum (MySQL-Funktionen – im Spiel nachgebaut)
                    YEAR('2023-01-15')   → 2023      MONTH(...) → 1     DAY(...) → 15
                    CURDATE()            → heutiges Datum      NOW() → jetzt mit Uhrzeit
                    DATEDIFF('2025-01-01', '2024-12-01')  → 31   (Tage, erstes minus zweites)
                    DATE_FORMAT('2023-01-15', '%d.%m.%Y') → 15.01.2023
                ! MySQL hat noch DATE_ADD(datum, INTERVAL 7 DAY), DAYNAME(), WEEK() ...
                ! SQLite-Original: strftime('%Y', datum), date('now'), julianday(...).
                ---
                # NULL ersetzen
                    COALESCE(a, b, c)    → der ERSTE Wert, der nicht NULL ist
                    IFNULL(a, 'x')       → a, oder 'x' falls a NULL ist   (MySQL & SQLite)
                    NULLIF(a, b)         → NULL, wenn a = b, sonst a  (z.B. gegen Division durch 0)

                # CAST – Typ umwandeln
                    CAST('42' AS INTEGER)       CAST(level AS DECIMAL(5,2))     CAST(wert AS CHAR)
                ! MySQL: CAST(x AS SIGNED) für Ganzzahl, CAST(x AS CHAR) für Text.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige name, wert und den Bruttopreis mit 19 % MwSt. (wert * 1.19), gerundet auf 2 Nachkommastellen, als `brutto`. Nur Gegenstände mit Wert.",
                    "loesung": "SELECT name, wert, ROUND(wert * 1.19, 2) AS brutto FROM gegenstaende WHERE wert IS NOT NULL;",
                    "spalten": True,
                },
                {
                    "aufgabe": "Zeige spieler_name und erstellt_am aller Spieler, die im Jahr 2023 erstellt wurden (benutze YEAR).",
                    "loesung": "SELECT spieler_name, erstellt_am FROM spieler WHERE YEAR(erstellt_am) = 2023;",
                    "muss_enthalten": ["YEAR"],
                },
                {
                    "aufgabe": "Zeige spieler_name und das Erstellungsdatum im deutschen Format TT.MM.JJJJ als `datum_de`.",
                    "loesung": "SELECT spieler_name, DATE_FORMAT(erstellt_am, '%d.%m.%Y') AS datum_de FROM spieler;",
                    "auch_richtig": ["SELECT spieler_name, strftime('%d.%m.%Y', erstellt_am) AS datum_de FROM spieler;"],
                    "spalten": True,
                    "hinweise": ["DATE_FORMAT(erstellt_am, '%d.%m.%Y')"],
                },
                {
                    "aufgabe": "Wie viele Tage war jeder Account am 01.01.2025 alt? Zeige spieler_name und `tage` (DATEDIFF).",
                    "loesung": "SELECT spieler_name, DATEDIFF('2025-01-01', erstellt_am) AS tage FROM spieler;",
                    "spalten": True,
                },
                {
                    "aufgabe": "Zeige name und beschreibung aller Gegenstände – wo die Beschreibung fehlt, soll 'Keine Beschreibung' stehen. Spalte `beschreibung`.",
                    "loesung": "SELECT name, COALESCE(beschreibung, 'Keine Beschreibung') AS beschreibung FROM gegenstaende;",
                    "auch_richtig": ["SELECT name, IFNULL(beschreibung, 'Keine Beschreibung') AS beschreibung FROM gegenstaende;"],
                    "spalten": True,
                },
            ],
        },
        {
            "titel": "UNION, INTERSECT, EXCEPT",
            "theorie": """
                # Ergebnisse untereinander hängen
                    SELECT spieler_name AS name FROM spieler
                    UNION
                    SELECT name FROM monster;

                * Beide SELECTs brauchen GLEICH VIELE Spalten mit passenden Typen.
                * Die Spaltennamen kommen vom ERSTEN SELECT.
                * `UNION` entfernt Duplikate, `UNION ALL` behält sie (und ist schneller).
                * ORDER BY nur EINMAL ganz am Ende – es sortiert das Gesamtergebnis.
                ---
                # Schnittmenge und Differenz
                    SELECT gegenstand_id FROM gegenstaende
                    EXCEPT                                  -- in der ersten, aber nicht in der zweiten
                    SELECT gegenstand_id FROM inventar;

                    SELECT gebiet FROM monster WHERE ist_boss = 0
                    INTERSECT                               -- in beiden
                    SELECT gebiet FROM monster WHERE stufe >= 9;

                ! INTERSECT und EXCEPT gibt es in MySQL erst ab Version 8.0.31. Vorher: mit IN / NOT IN (Kapitel 8).
                ! Oracle nennt EXCEPT übrigens MINUS.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Erstelle EINE Liste aller Namen von Spielern und Monstern (eine Spalte `name`), alphabetisch sortiert.",
                    "loesung": "SELECT spieler_name AS name FROM spieler UNION SELECT name FROM monster ORDER BY name;",
                    "spalten": True,
                    "hinweise": ["SELECT spieler_name AS name FROM spieler UNION SELECT name FROM monster ORDER BY name;"],
                },
                {
                    "aufgabe": "Liste alle gebiet-Werte der Monster und dahinter alle typ-Werte der Gegenstände in EINER Spalte `eintrag` – Duplikate sollen ERHALTEN bleiben.",
                    "loesung": "SELECT gebiet AS eintrag FROM monster UNION ALL SELECT typ FROM gegenstaende;",
                    "spalten": True,
                    "muss_enthalten": ["UNION ALL"],
                },
                {
                    "aufgabe": "Welche gegenstand_id kommen in keinem Inventar vor? Benutze EXCEPT.",
                    "loesung": "SELECT gegenstand_id FROM gegenstaende EXCEPT SELECT gegenstand_id FROM inventar;",
                    "muss_enthalten": ["EXCEPT"],
                },
                {
                    "aufgabe": "Welche Gebiete haben sowohl ein Monster unter Stufe 5 als auch eines ab Stufe 5? (INTERSECT)",
                    "loesung": "SELECT gebiet FROM monster WHERE stufe < 5 INTERSECT SELECT gebiet FROM monster WHERE stufe >= 5;",
                    "muss_enthalten": ["INTERSECT"],
                },
            ],
        },
        {
            "titel": "VIEWs – gespeicherte Abfragen",
            "theorie": """
                # Eine View ist eine "virtuelle Tabelle"
                    CREATE VIEW top_spieler AS
                    SELECT spieler_name, klasse, level
                    FROM spieler
                    WHERE level >= 15;

                    SELECT * FROM top_spieler;     -- benutzen wie eine Tabelle
                    DROP VIEW top_spieler;         -- löschen

                * Eine View speichert NUR die Abfrage, keine Daten. Ändert sich `spieler`,
                  zeigt die View sofort die neuen Daten.
                * Nutzen: komplizierte Abfragen wiederverwenden, Spalten verstecken (Sicherheit:
                  man gibt Nutzern nur Rechte auf die View, nicht auf die Tabelle).
                ! MySQL: `CREATE OR REPLACE VIEW name AS ...` überschreibt eine bestehende View.
            """,
            "aufgaben": [
                {
                    "typ": "aendern",
                    "aufgabe": "Erstelle die View `top_spieler` mit spieler_name, klasse, level aller Spieler ab Level 15.",
                    "loesung": "CREATE VIEW top_spieler AS SELECT spieler_name, klasse, level FROM spieler WHERE level >= 15;",
                    "pruefung": [VIEWS, "SELECT * FROM top_spieler"],
                },
                {
                    "aufgabe": "Die View `waffen_liste` existiert schon (name, wert aller Waffen). Frag sie ab: alle Waffen über 1000 Wert, teuerste zuerst.",
                    "setup": "CREATE VIEW waffen_liste AS SELECT name, wert FROM gegenstaende WHERE typ = 'Waffe';",
                    "loesung": "SELECT * FROM waffen_liste WHERE wert > 1000 ORDER BY wert DESC;",
                    "hinweise": ["Eine View fragt man ab wie eine Tabelle: SELECT * FROM waffen_liste ..."],
                },
                {
                    "typ": "aendern",
                    "aufgabe": "Die View `waffen_liste` wird nicht mehr gebraucht – entferne sie.",
                    "setup": "CREATE VIEW waffen_liste AS SELECT name, wert FROM gegenstaende WHERE typ = 'Waffe';",
                    "loesung": "DROP VIEW waffen_liste;",
                    "pruefung": VIEWS,
                },
            ],
        },
    ],
    "boss": {
        "titel": "Der Chronist",
        "story": """
            # Der Chronist schreibt das Buch der Helden.
            Er will eine schön formatierte Top-10-Liste.
        """,
        "aufgabe": """
            Zeige die 10 Spieler mit dem höchsten Level (bei Gleichstand alphabetisch nach Name) mit den Spalten:
              held          → Name in Großbuchstaben
              titel         → 'Legende' ab Level 18, 'Held' ab Level 12, sonst 'Abenteurer'
              gilde_status  → 'gildenlos', wenn keine Gilde, sonst 'Gilde ' + gilde_id   (z.B. 'Gilde 3')
              seit_jahr     → das Jahr der Account-Erstellung
        """,
        "loesung": """SELECT UPPER(spieler_name) AS held,
                CASE WHEN level >= 18 THEN 'Legende' WHEN level >= 12 THEN 'Held' ELSE 'Abenteurer' END AS titel,
                CASE WHEN gilde_id IS NULL THEN 'gildenlos' ELSE CONCAT('Gilde ', gilde_id) END AS gilde_status,
                YEAR(erstellt_am) AS seit_jahr
            FROM spieler
            ORDER BY level DESC, spieler_name
            LIMIT 10;""",
        "auch_richtig": ["""SELECT UPPER(spieler_name) AS held,
                CASE WHEN level >= 18 THEN 'Legende' WHEN level >= 12 THEN 'Held' ELSE 'Abenteurer' END AS titel,
                COALESCE('Gilde ' || gilde_id, 'gildenlos') AS gilde_status,
                CAST(strftime('%Y', erstellt_am) AS INTEGER) AS seit_jahr
            FROM spieler ORDER BY level DESC, spieler_name LIMIT 10;"""],
        "spalten": True,
        "hinweise": ["Vier Spalten: UPPER(...), CASE ..., CASE WHEN gilde_id IS NULL ..., YEAR(...)",
                     "ORDER BY level DESC, spieler_name LIMIT 10"],
    },
}
