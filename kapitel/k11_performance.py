from ._hilfe import indizes

KAPITEL = {
    "nr": 11,
    "titel": "Performance",
    "lektionen": [
        {
            "titel": "Wie sucht eine Datenbank?",
            "theorie": """
                # Full Table Scan
                    SELECT * FROM spieler WHERE spieler_name = 'FireMage';
                Ohne Hilfe muss die DB JEDE Zeile anschauen ("Full Table Scan").
                Bei 18 Spielern egal – bei 18 Millionen dauert das Sekunden bis Minuten.

                # Index = das Stichwortverzeichnis eines Buches
                Statt das ganze Buch zu lesen, schaust du hinten im Register nach: "Drache … Seite 42".
                Ein Index speichert die Werte einer Spalte SORTIERT mit Verweis auf die Zeile.
                * Meist als B-Baum (B-Tree): Suche in log(n) Schritten – 1 Mio. Zeilen ≈ 20 Schritte statt 1 Mio.
                * Primärschlüssel und UNIQUE-Spalten bekommen automatisch einen Index.
                * Fremdschlüssel bekommen in MySQL (InnoDB) automatisch einen Index, in SQLite NICHT.
                ---
                # Wann hilft ein Index?
                ✔ Spalten in WHERE, JOIN ... ON, ORDER BY, GROUP BY, die oft abgefragt werden
                ✔ Spalten mit vielen verschiedenen Werten (hohe Selektivität: E-Mail, Name, Datum)
                ✘ Spalten mit wenigen Werten (ist_boss: 0/1) – da liest die DB eh die halbe Tabelle
                ✘ Sehr kleine Tabellen
                ✘ Tabellen mit extrem vielen Schreibzugriffen (jeder INSERT/UPDATE/DELETE muss
                  auch JEDEN Index aktualisieren → Schreiben wird langsamer, Speicher wächst)
            """,
            "aufgaben": [
                {
                    "typ": "quiz",
                    "aufgabe": "Was ist der Hauptnachteil eines Index?",
                    "optionen": ["SELECTs werden langsamer",
                                 "INSERT/UPDATE/DELETE werden langsamer und er braucht Speicherplatz",
                                 "Die Daten werden unsortiert",
                                 "Man kann keine Fremdschlüssel mehr nutzen"],
                    "richtig": 2,
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Für welche Spalte lohnt sich ein Index am WENIGSTEN?",
                    "optionen": ["kunden.email (wird beim Login gesucht)",
                                 "bestellungen.datum (wird oft nach Zeitraum gefiltert)",
                                 "monster.ist_boss (nur 0 oder 1)",
                                 "inventar.spieler_id (wird ständig gejoint)"],
                    "richtig": 3,
                    "erklaerung": "Bei nur 2 verschiedenen Werten ist die Selektivität zu gering – ein Scan ist ähnlich schnell.",
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Welche Spalten haben automatisch einen Index?",
                    "optionen": ["Alle Spalten", "PRIMARY KEY und UNIQUE", "Nur Textspalten", "Keine"],
                    "richtig": 2,
                },
            ],
        },
        {
            "titel": "CREATE INDEX",
            "theorie": """
                # Index anlegen
                    CREATE INDEX idx_spieler_klasse ON spieler (klasse);
                    CREATE UNIQUE INDEX idx_gegenstand_name ON gegenstaende (name);   -- + Eindeutigkeit
                    CREATE INDEX idx_monster_gebiet_stufe ON monster (gebiet, stufe); -- zusammengesetzt

                    DROP INDEX idx_spieler_klasse;                -- SQLite / Standard
                ! MySQL: `DROP INDEX idx_spieler_klasse ON spieler;`
                ! MySQL: `SHOW INDEX FROM spieler;` zeigt alle Indizes (geht hier auch).
                ! MySQL: Index direkt im CREATE TABLE: `INDEX idx_name (spalte)` als eigene Zeile.

                ? Namenskonvention: idx_tabelle_spalte(n)
                ---
                # Zusammengesetzter Index & die Linkspräfix-Regel
                Ein Index auf (gebiet, stufe) ist sortiert wie ein Telefonbuch (Nachname, Vorname):
                ✔ WHERE gebiet = 'Elchwald'                     – nutzt den Index
                ✔ WHERE gebiet = 'Elchwald' AND stufe > 2        – nutzt den Index komplett
                ✘ WHERE stufe > 2                               – Index NICHT nutzbar!
                  (Im Telefonbuch alle "Max" finden? Muss man alles durchlesen.)
                → Die Spalte, nach der am häufigsten allein gefiltert wird, gehört nach vorne.
            """,
            "aufgaben": [
                {
                    "typ": "aendern",
                    "aufgabe": "Lege einen Index auf die Spalte `klasse` der Tabelle `spieler` an (Name z.B. idx_spieler_klasse).",
                    "loesung": "CREATE INDEX idx_spieler_klasse ON spieler (klasse);",
                    "pruefung": indizes("spieler"),
                },
                {
                    "typ": "aendern",
                    "aufgabe": "Lege einen EINDEUTIGEN Index auf `name` in `gegenstaende` an, damit kein Gegenstandsname doppelt vorkommen kann.",
                    "loesung": "CREATE UNIQUE INDEX idx_gegenstand_name ON gegenstaende (name);",
                    "auch_richtig": ["ALTER TABLE gegenstaende ADD UNIQUE INDEX idx_gname (name);"],
                    "tests": ["INSERT INTO gegenstaende (name, typ) VALUES ('Heiltrank', 'Trank')"],
                    "pruefung": indizes("gegenstaende"),
                },
                {
                    "typ": "aendern",
                    "aufgabe": "Lege einen zusammengesetzten Index auf `monster` an: zuerst `gebiet`, dann `stufe`.",
                    "loesung": "CREATE INDEX idx_monster_gebiet_stufe ON monster (gebiet, stufe);",
                    "pruefung": indizes("monster"),
                },
                {
                    "typ": "aendern",
                    "setup": "CREATE INDEX idx_alt ON quests (titel);",
                    "aufgabe": "Der Index `idx_alt` auf quests wird nicht gebraucht. Lösche ihn.",
                    "loesung": "DROP INDEX idx_alt;",
                    "auch_richtig": ["DROP INDEX idx_alt ON quests;"],
                    "pruefung": indizes("quests"),
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Es gibt einen Index auf (gebiet, stufe). Welche Abfrage kann ihn NICHT nutzen?",
                    "optionen": ["WHERE gebiet = 'Elchwald'",
                                 "WHERE gebiet = 'Elchwald' AND stufe = 3",
                                 "WHERE stufe = 3",
                                 "WHERE gebiet = 'Elchwald' ORDER BY stufe"],
                    "richtig": 3,
                    "erklaerung": "Linkspräfix-Regel: ohne die erste Index-Spalte (gebiet) ist der Index nicht nutzbar.",
                },
            ],
        },
        {
            "titel": "EXPLAIN – in die Datenbank hineinschauen",
            "theorie": """
                # Wie führt die DB meine Abfrage aus?
                    EXPLAIN SELECT * FROM monster WHERE gebiet = 'Elchwald';

                ! MySQL: `EXPLAIN SELECT ...` zeigt eine Tabelle. Wichtige Spalten:
                !   type: ALL = Full Table Scan (schlecht), ref/range/const = Index (gut)
                !   key: welcher Index benutzt wird, rows: geschätzte Anzahl gelesener Zeilen
                SQLite heißt es `EXPLAIN QUERY PLAN` (das Spiel übersetzt `EXPLAIN` automatisch):
                    SCAN monster                                → liest die ganze Tabelle
                    SEARCH monster USING INDEX idx (gebiet=?)   → springt per Index direkt hin
                ---
                # Wann ein Index NICHT benutzt werden kann
                ✘ Funktion auf der Spalte:     WHERE YEAR(erstellt_am) = 2023
                  ✔ besser:                    WHERE erstellt_am BETWEEN '2023-01-01' AND '2023-12-31'
                ✘ Rechnung auf der Spalte:     WHERE level + 1 > 10
                  ✔ besser:                    WHERE level > 9
                ✘ LIKE mit % am Anfang:        WHERE name LIKE '%klinge'
                  ✔ (nutzbar):                 WHERE name LIKE 'Feuer%'
                ✘ Linkspräfix fehlt (siehe vorige Lektion)
                ✘ OR über verschiedene Spalten (oft)
                Merke: Die indizierte Spalte muss "nackt" auf einer Seite des Vergleichs stehen.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Lass dir den Ausführungsplan von `SELECT * FROM monster WHERE gebiet = 'Elchwald';` anzeigen. (Ohne Index – du wirst SCAN sehen.)",
                    "loesung": "EXPLAIN QUERY PLAN SELECT * FROM monster WHERE gebiet = 'Elchwald';",
                    "auch_richtig": ["EXPLAIN SELECT * FROM monster WHERE gebiet = 'Elchwald';"],
                    "hinweise": ["EXPLAIN vor das SELECT schreiben."],
                },
                {
                    "typ": "aendern",
                    "aufgabe": "Sorge mit einem passenden Index dafür, dass `SELECT * FROM monster WHERE gebiet = 'Elchwald'` kein SCAN mehr ist, sondern ein SEARCH. Prüfe danach mit EXPLAIN.",
                    "loesung": "CREATE INDEX idx_monster_gebiet ON monster (gebiet);",
                    "auch_richtig": ["CREATE INDEX idx_x ON monster (gebiet, stufe);"],
                    "pruefung": "PLAN SELECT * FROM monster WHERE gebiet = 'Elchwald'",
                },
                {
                    "setup": "CREATE INDEX idx_spieler_erstellt ON spieler (erstellt_am);",
                    "aufgabe": """
                        Es gibt einen Index auf spieler(erstellt_am). Diese Abfrage kann ihn aber nicht nutzen:
                            SELECT spieler_name FROM spieler WHERE YEAR(erstellt_am) = 2023;
                        Schreib sie so um, dass sie dasselbe liefert UND den Index benutzt.
                    """,
                    "loesung": "SELECT spieler_name FROM spieler WHERE erstellt_am BETWEEN '2023-01-01' AND '2023-12-31';",
                    "auch_richtig": ["SELECT spieler_name FROM spieler WHERE erstellt_am >= '2023-01-01' AND erstellt_am < '2024-01-01';"],
                    "falsch": ["SELECT spieler_name FROM spieler WHERE YEAR(erstellt_am) = 2023;"],
                    "plan": True,
                    "hinweise": ["Keine Funktion um die Spalte!", "WHERE erstellt_am BETWEEN '2023-01-01' AND '2023-12-31'"],
                },
                {
                    "setup": "CREATE INDEX idx_spieler_level ON spieler (level);",
                    "aufgabe": """
                        Index auf spieler(level). Schreib diese Abfrage index-freundlich um:
                            SELECT spieler_name, level FROM spieler WHERE level * 2 >= 30;
                    """,
                    "loesung": "SELECT spieler_name, level FROM spieler WHERE level >= 15;",
                    "falsch": ["SELECT spieler_name, level FROM spieler WHERE level * 2 >= 30;"],
                    "plan": True,
                    "hinweise": ["Rechne die Bedingung um: level * 2 >= 30  ⇔  level >= 15"],
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Index auf gegenstaende(name). Welche Bedingung kann den Index nutzen?",
                    "optionen": ["WHERE name LIKE '%schwert'", "WHERE UPPER(name) = 'HEILTRANK'", "WHERE name LIKE 'Heil%'", "WHERE LENGTH(name) > 5"],
                    "richtig": 3,
                },
            ],
        },
        {
            "titel": "Gute Abfragen schreiben",
            "theorie": """
                # Best Practices
                * Nur die Spalten holen, die man braucht – kein `SELECT *` im Programmcode.
                * So früh wie möglich filtern (WHERE vor HAVING, wenn es geht).
                * LIMIT bei Listen/Paging. Bei riesigen OFFSETs wird es langsam
                  → "Keyset-Pagination": `WHERE id > letzte_id ORDER BY id LIMIT 20`.
                * Fremdschlüssel-Spalten indizieren, über die gejoint wird.
                * `EXISTS` statt `COUNT(*) > 0`, wenn man nur wissen will, OB es etwas gibt
                  (EXISTS hört beim ersten Treffer auf).
                * `UNION ALL` statt `UNION`, wenn Duplikate egal/unmöglich sind (spart das Sortieren).
                * Viele INSERTs in EINER Transaktion bündeln (statt 1000 einzelne Commits).
                ---
                # Das N+1-Problem (typisch in Programmen)
                    -- 1 Abfrage für alle Gilden ...
                    SELECT * FROM gilden;
                    -- ... und dann im Programm in einer Schleife für JEDE Gilde:
                    SELECT * FROM spieler WHERE gilde_id = ?;     -- N weitere Abfragen!
                Bei 1000 Gilden = 1001 Abfragen. Besser: EIN JOIN (oder `WHERE gilde_id IN (...)`).
                ---
                # Weitere Stellschrauben (nur zum Wissen)
                * Normalisierung vs. Denormalisierung: Normalisiert = weniger Redundanz, mehr JOINs.
                  Für Reports darf man bewusst denormalisieren (vorberechnete Summen, Views).
                * Datentypen klein halten (INT statt BIGINT, wenn es reicht; kein TEXT für 2 Zeichen).
                * Partitionierung, Caching, Read-Replicas – Themen für sehr große Systeme.
            """,
            "aufgaben": [
                {
                    "typ": "quiz",
                    "aufgabe": "Ein Programm lädt 500 Spieler und fragt danach für JEDEN Spieler einzeln sein Inventar ab. Wie heißt das Problem?",
                    "optionen": ["Deadlock", "N+1-Problem", "Kartesisches Produkt", "Löschanomalie"],
                    "richtig": 2,
                    "erklaerung": "1 + 500 Abfragen. Lösung: ein JOIN zwischen spieler und inventar.",
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Du willst nur wissen, OB ein Spieler überhaupt einen Gegenstand hat. Was ist am effizientesten?",
                    "optionen": ["SELECT COUNT(*) FROM inventar WHERE spieler_id = 5  (und dann > 0 prüfen)",
                                 "SELECT * FROM inventar  (und im Programm suchen)",
                                 "SELECT EXISTS (SELECT 1 FROM inventar WHERE spieler_id = 5)",
                                 "SELECT SUM(anzahl) FROM inventar"],
                    "richtig": 3,
                },
                {
                    "aufgabe": "Index-freundlich und sparsam: Zeige NUR spieler_name und level der 5 höchstleveligen Magier.",
                    "loesung": "SELECT spieler_name, level FROM spieler WHERE klasse = 'Magier' ORDER BY level DESC LIMIT 5;",
                },
                {
                    "aufgabe": "Ersetze das N+1-Muster durch EINE Abfrage: gildenname und spieler_name aller Gildenmitglieder, sortiert nach gildenname, spieler_name.",
                    "loesung": "SELECT g.gildenname, s.spieler_name FROM gilden g JOIN spieler s ON s.gilde_id = g.gilde_id ORDER BY g.gildenname, s.spieler_name;",
                },
            ],
        },
        {
            "titel": "Sicherheit, Rechte (DCL) & SQL-Injection",
            "theorie": """
                # Benutzer und Rechte (DCL, MySQL)
                    CREATE USER 'shop_app'@'localhost' IDENTIFIED BY 'geheim';
                    GRANT SELECT, INSERT, UPDATE ON rpg_spielwelt.* TO 'shop_app'@'localhost';
                    GRANT SELECT ON rpg_spielwelt.top_spieler TO 'praktikant'@'%';    -- nur eine View
                    REVOKE UPDATE ON rpg_spielwelt.* FROM 'shop_app'@'localhost';
                    SHOW GRANTS FOR 'shop_app'@'localhost';
                    DROP USER 'praktikant'@'%';

                * Prinzip der minimalen Rechte (Least Privilege): Eine App bekommt nur, was sie braucht –
                  niemals root/ALL PRIVILEGES.
                * Rollen (MySQL 8): Rechte an eine Rolle geben, Rolle an Benutzer.
                ? SQLite hat keine Benutzer – darum hier nur Theorie.
                ---
                # SQL-Injection – die gefährlichste Lücke
                Ein Programm baut SQL aus Benutzereingaben zusammen:
                    sql = "SELECT * FROM accounts WHERE email = '" + eingabe + "'"
                Der Angreifer tippt:   ' OR '1'='1
                    SELECT * FROM accounts WHERE email = '' OR '1'='1'     → ALLE Accounts!
                Oder:  '; DROP TABLE accounts; --

                # Schutz: Prepared Statements (Parameter)
                    cursor.execute("SELECT * FROM accounts WHERE email = ?", (eingabe,))     -- Python
                    $stmt = $pdo->prepare("SELECT * FROM accounts WHERE email = :email");  -- PHP
                Die Eingabe wird IMMER als Wert behandelt, nie als SQL-Code.
                * Zusätzlich: Eingaben validieren, minimale DB-Rechte, Fehlermeldungen nicht an Nutzer zeigen.
                * Passwörter NIE im Klartext speichern → Hash (bcrypt/argon2) mit Salt.
            """,
            "aufgaben": [
                {
                    "typ": "quiz",
                    "aufgabe": "Welcher Befehl entzieht einem Benutzer ein Recht?",
                    "optionen": ["DENY", "REVOKE", "REMOVE", "DROP GRANT"],
                    "richtig": 2,
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Was schützt am zuverlässigsten vor SQL-Injection?",
                    "optionen": ["Anführungszeichen im Code verdoppeln",
                                 "Prepared Statements / parametrisierte Abfragen",
                                 "Eingaben in Großbuchstaben umwandeln",
                                 "Die Datenbank auf einem anderen Server betreiben"],
                    "richtig": 2,
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Ein Webshop verbindet sich mit dem root-Benutzer zur DB. Welches Prinzip wird verletzt?",
                    "optionen": ["ACID", "Normalisierung", "Least Privilege (minimale Rechte)", "Referentielle Integrität"],
                    "richtig": 3,
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Der Login prüft `... WHERE name = '<eingabe>' AND passwort = '<eingabe2>'`. Ein Angreifer gibt als Name `admin' --` ein. Was passiert?",
                    "optionen": ["Nichts, der Name existiert nicht",
                                 "Der Rest der Zeile (Passwortprüfung) wird zum Kommentar – Login als admin ohne Passwort",
                                 "Die Datenbank stürzt ab",
                                 "Der Benutzer admin wird gelöscht"],
                    "richtig": 2,
                },
            ],
        },
    ],
    "boss": {
        "titel": "Der Zeitfresser",
        "story": """
            # Ein Fluch lässt die Server stöhnen!
            Zwei Abfragen laufen ständig und machen Full Table Scans. Brich den Fluch mit den richtigen Indizes.
        """,
        "typ": "aendern",
        "aufgabe": """
            Diese beiden Abfragen laufen tausendmal pro Minute:
              A)  SELECT g.name, i.anzahl FROM inventar i JOIN gegenstaende g ON g.gegenstand_id = i.gegenstand_id
                  WHERE i.spieler_id = 9;
              B)  SELECT name, stufe FROM monster WHERE gebiet = 'Verlassene Gruft' AND stufe >= 5;
            Lege Indizes an, sodass KEINE der beiden Abfragen mehr einen SCAN auf inventar bzw. monster braucht
            (Abfrage B soll dabei sowohl gebiet als auch stufe über den Index finden).
            Prüfe deine Lösung vorher mit EXPLAIN!
        """,
        "loesung": """CREATE INDEX idx_inventar_spieler ON inventar (spieler_id);
            CREATE INDEX idx_monster_gebiet_stufe ON monster (gebiet, stufe);""",
        "auch_richtig": ["""CREATE INDEX a ON inventar (spieler_id, gegenstand_id);
            CREATE INDEX b ON monster (gebiet, stufe);"""],
        "pruefung": ["PLAN SELECT g.name, i.anzahl FROM inventar i JOIN gegenstaende g ON g.gegenstand_id = i.gegenstand_id WHERE i.spieler_id = 9",
                     "PLAN SELECT name, stufe FROM monster WHERE gebiet = 'Verlassene Gruft' AND stufe >= 5"],
        "falsch": ["CREATE INDEX x ON inventar (spieler_id); CREATE INDEX y ON monster (stufe, gebiet);",
                   "CREATE INDEX x ON inventar (spieler_id); CREATE INDEX y ON monster (gebiet);"],
        "hinweise": ["Abfrage A filtert inventar nach spieler_id.",
                     "Abfrage B: zusammengesetzter Index – die Spalte mit '=' gehört nach vorne: (gebiet, stufe)."],
    },
}
