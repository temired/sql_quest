from ._hilfe import spalten, spaltennamen, TABELLEN

KAPITEL = {
    "nr": 2,
    "titel": "Tabellen (DDL)",
    "lektionen": [
        {
            "titel": "Datentypen",
            "theorie": """
                # Jede Spalte hat einen Datentyp
                Der Typ legt fest, was in eine Spalte darf und wie viel Platz sie braucht.

                    Typ              | Bedeutung                         | Beispiel
                    -----------------+-----------------------------------+--------------------
                    INT / INTEGER    | Ganzzahl (ca. ±2,1 Mrd.)          | level, anzahl, IDs
                    BIGINT           | sehr große Ganzzahl               | Klickzähler
                    TINYINT/SMALLINT | kleine Ganzzahl                   | Alter
                    DECIMAL(p,s)     | exakte Kommazahl, p Stellen       | Preis DECIMAL(10,2)
                                     |   gesamt, davon s nach dem Komma  |   → 12345678.99
                    FLOAT / DOUBLE   | ungefähre Kommazahl (Rundungs-    | Messwerte, Koordinaten
                                     |   fehler möglich!)                |
                    CHAR(n)          | Text mit FESTER Länge n           | PLZ CHAR(5), Land CHAR(2)
                    VARCHAR(n)       | Text mit VARIABLER Länge, max n   | Namen VARCHAR(50)
                    TEXT             | langer Text                       | Beschreibung
                    DATE             | Datum 'JJJJ-MM-TT'                | '2026-11-04'
                    TIME             | Uhrzeit 'hh:mm:ss'                | '14:30:00'
                    DATETIME         | Datum + Uhrzeit                   | '2026-11-04 14:30:00'
                    BOOLEAN          | wahr/falsch (MySQL: TINYINT(1))   | ist_boss
                    ENUM('a','b')    | nur MySQL: einer aus einer Liste  | ENUM('Krieger','Magier')
                ---
                # Typ-Wahl: die klassischen Prüfungsfallen
                * Geld IMMER als DECIMAL – nie FLOAT (0.1 + 0.2 ≠ 0.3 bei FLOAT!).
                * Postleitzahl, Telefonnummer, IBAN → Text (CHAR/VARCHAR), nicht INT!
                  Man rechnet nicht damit, und führende Nullen ('01067') würden verschwinden.
                * Datum als DATE, nicht als VARCHAR – sonst kann man nicht damit rechnen/sortieren.
                * VARCHAR(n) großzügig, aber sinnvoll wählen (E-Mail: VARCHAR(255)).
                ---
                # VARCHAR oder TEXT?
                Beides speichert Text – aber:
                * `VARCHAR(50)` = Text mit einer HÖCHSTlänge (hier 50 Zeichen). Der Normalfall für Namen,
                  Städte, E-Mails, Titel … Die DB prüft die Länge, und man kann gut danach suchen/sortieren.
                * `TEXT` = langer Text OHNE sinnvolle Höchstlänge: Beschreibungen, Kommentare, Artikel.
                  In MySQL schreibt man TEXT ohne Zahl dahinter.

                ? So sind die Aufgaben formuliert: "Zeichenkette bis 50 Zeichen" heißt `VARCHAR(50)`.
                ? "Ganzzahl" heißt `INT`, "Datum" heißt `DATE`, "wahr/falsch" heißt `BOOLEAN`.

                ? SQLite ist beim Typ sehr locker (es speichert fast alles überall). MySQL ist streng.
                ? Schreib im Spiel trotzdem immer die richtigen MySQL-Typen – das wird geprüft.
            """,
            "aufgaben": [
                {
                    "typ": "quiz",
                    "aufgabe": "Welcher Datentyp passt am besten für den Preis eines Gegenstands in Euro?",
                    "optionen": ["FLOAT", "INT", "DECIMAL(10,2)", "VARCHAR(10)"],
                    "richtig": 3,
                    "erklaerung": "DECIMAL rechnet exakt – wichtig bei Geld. FLOAT hat Rundungsfehler.",
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Welcher Datentyp passt für eine deutsche Postleitzahl (z.B. 01067)?",
                    "optionen": ["INT", "CHAR(5)", "DECIMAL(5,0)", "DATE"],
                    "richtig": 2,
                    "erklaerung": "Mit INT würde aus 01067 die Zahl 1067. PLZ sind feste 5 Zeichen → CHAR(5).",
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Was ist der Unterschied zwischen CHAR(10) und VARCHAR(10)?",
                    "optionen": ["Keiner",
                                 "CHAR belegt immer 10 Zeichen (wird aufgefüllt), VARCHAR nur so viele wie nötig",
                                 "VARCHAR kann nur Zahlen speichern",
                                 "CHAR kann längere Texte als VARCHAR speichern"],
                    "richtig": 2,
                    "erklaerung": "CHAR = feste Länge (gut für immer gleich lange Werte), VARCHAR = variable Länge bis max. n.",
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Was bedeutet DECIMAL(6,2)?",
                    "optionen": ["6 Stellen vor und 2 nach dem Komma",
                                 "6 Stellen insgesamt, davon 2 nach dem Komma (max. 9999.99)",
                                 "Werte von 2 bis 6",
                                 "6 Nachkommastellen, gerundet auf 2"],
                    "richtig": 2,
                    "erklaerung": "p = Gesamtstellen, s = Nachkommastellen. DECIMAL(6,2) → größter Wert 9999.99.",
                },
            ],
        },
        {
            "titel": "CREATE TABLE",
            "theorie": """
                # Eine Tabelle anlegen
                    CREATE TABLE haendler (
                        haendler_id  INT,
                        name         VARCHAR(50),
                        stadt        VARCHAR(50)
                    );

                * Nach `CREATE TABLE name (` folgt pro Spalte: `spaltenname DATENTYP`
                * Spalten mit Komma trennen – nach der LETZTEN Spalte kein Komma!
                * Am Ende `);`
                * Tabellen- und Spaltennamen: klein, ohne Leerzeichen/Umlaute, mit `_` (snake_case).
                * Jede Spalte MUSS einen Datentyp haben – `haendler_id,` allein ist ein Fehler.

                ? Zusätze wie `PRIMARY KEY`, `AUTO_INCREMENT`, `NOT NULL` oder `DEFAULT` lernst du in Kapitel 3
                ? (Constraints). In diesem Kapitel brauchst du nur Spaltenname + Datentyp. Schreibst du sie trotzdem
                ? dazu, ist das kein Fehler.

                    CREATE TABLE IF NOT EXISTS haendler ( ... );
                `IF NOT EXISTS` verhindert einen Fehler, falls es die Tabelle schon gibt.
                ---
                # MySQL: Datenbank anlegen
                    CREATE DATABASE rpg_spielwelt;
                    CREATE DATABASE IF NOT EXISTS rpg_spielwelt
                        DEFAULT CHARACTER SET utf8mb4;
                    USE rpg_spielwelt;
                    DROP DATABASE rpg_spielwelt;   -- löscht ALLES darin!

                ! `utf8mb4` ist der richtige Zeichensatz in MySQL (kann auch Emojis). `utf8` ist veraltet.

                ? Im Terminal-Modus tippst du lange Befehle bequemer in die Datei antwort.sql und gibst sie mit .d ab.
                ? (Das ist eine Spielfunktion, kein SQL. In der Browser-Oberfläche schreibst du einfach in den Editor.)
            """,
            "aufgaben": [
                {
                    "typ": "aendern",
                    "aufgabe": """
                        Lege die Tabelle `haendler` an mit den Spalten (in dieser Reihenfolge):
                          haendler_id  → Ganzzahl
                          name         → Zeichenkette bis 50 Zeichen
                          stadt        → Zeichenkette bis 50 Zeichen
                    """,
                    "loesung": "CREATE TABLE haendler (haendler_id INT, name VARCHAR(50), stadt VARCHAR(50));",
                    "pruefung": spalten("haendler"),
                    "hinweise": ["CREATE TABLE haendler ( ... );", "haendler_id INT, name VARCHAR(50), ..."],
                },
                {
                    "typ": "aendern",
                    "aufgabe": """
                        Lege die Tabelle `haustiere` an:
                          tier_id     → Ganzzahl
                          name        → Zeichenkette bis 30 Zeichen
                          art         → Zeichenkette bis 30 Zeichen
                          geburtstag  → Datum
                          gewicht_kg  → exakte Kommazahl, 5 Stellen gesamt, 2 nach dem Komma
                          ist_zahm    → wahr/falsch
                    """,
                    "loesung": """CREATE TABLE haustiere (
                        tier_id INT, name VARCHAR(30), art VARCHAR(30),
                        geburtstag DATE, gewicht_kg DECIMAL(5,2), ist_zahm BOOLEAN);""",
                    "pruefung": spalten("haustiere"),
                    "hinweise": ["Typen: INT, VARCHAR(30), DATE, DECIMAL(5,2), BOOLEAN"],
                },
                {
                    "typ": "aendern",
                    "aufgabe": """
                        Lege die Tabelle `turniere` an – aber so, dass KEIN Fehler kommt, falls sie schon existiert:
                          turnier_id → Ganzzahl, name → Zeichenkette bis 80 Zeichen, datum → Datum, preisgeld → DECIMAL(10,2)
                        (Im Hintergrund existiert die Tabelle bereits mit genau diesen Spalten.)
                    """,
                    "setup": "CREATE TABLE turniere (turnier_id INT, name VARCHAR(80), datum DATE, preisgeld DECIMAL(10,2));",
                    "loesung": "CREATE TABLE IF NOT EXISTS turniere (turnier_id INT, name VARCHAR(80), datum DATE, preisgeld DECIMAL(10,2));",
                    "pruefung": spalten("turniere"),
                    "muss_enthalten": ["IF NOT EXISTS"],
                    "hinweise": ["CREATE TABLE IF NOT EXISTS ..."],
                },
            ],
        },
        {
            "titel": "ALTER TABLE",
            "theorie": """
                # Bestehende Tabellen ändern
                    -- Spalte hinzufügen
                    ALTER TABLE spieler ADD COLUMN gold INT DEFAULT 0;

                    -- Spalte umbenennen
                    ALTER TABLE gilden RENAME COLUMN gruendungsjahr TO gegruendet;

                    -- Spalte löschen (Daten darin sind weg!)
                    ALTER TABLE gegenstaende DROP COLUMN beschreibung;

                    -- Tabelle umbenennen
                    ALTER TABLE monster RENAME TO kreaturen;

                ! MySQL kann zusätzlich den Typ ändern:
                !   `ALTER TABLE spieler MODIFY COLUMN klasse VARCHAR(40) NOT NULL;`
                !   `ALTER TABLE spieler CHANGE alter_name neuer_name VARCHAR(40);`
                ! und hat `RENAME TABLE monster TO kreaturen;` (versteht das Spiel auch).
                ! Das Wort COLUMN ist bei ADD/DROP in MySQL optional.
            """,
            "aufgaben": [
                {
                    "typ": "aendern",
                    "aufgabe": "Füge der Tabelle `spieler` die Spalte `gold` (Ganzzahl) hinzu, Standardwert 0.",
                    "loesung": "ALTER TABLE spieler ADD COLUMN gold INT DEFAULT 0;",
                    "pruefung": [spalten("spieler"), "SELECT spieler_id, gold FROM spieler ORDER BY spieler_id"],
                    "hinweise": ["ALTER TABLE ... ADD COLUMN ...", "DEFAULT 0 hinter den Typ schreiben."],
                    "erklaerung": "Alle bestehenden Spieler haben jetzt automatisch gold = 0 (der DEFAULT-Wert).",
                },
                {
                    "typ": "aendern",
                    "aufgabe": "Benenne in `gilden` die Spalte `gruendungsjahr` in `gegruendet` um.",
                    "loesung": "ALTER TABLE gilden RENAME COLUMN gruendungsjahr TO gegruendet;",
                    "pruefung": spaltennamen("gilden"),
                    "hinweise": ["ALTER TABLE ... RENAME COLUMN alt TO neu;"],
                },
                {
                    "typ": "aendern",
                    "aufgabe": "Entferne aus `gegenstaende` die Spalte `beschreibung`.",
                    "loesung": "ALTER TABLE gegenstaende DROP COLUMN beschreibung;",
                    "pruefung": spaltennamen("gegenstaende"),
                    "hinweise": ["ALTER TABLE ... DROP COLUMN ...;"],
                },
                {
                    "typ": "aendern",
                    "aufgabe": "Benenne die Tabelle `monster` in `kreaturen` um.",
                    "loesung": "ALTER TABLE monster RENAME TO kreaturen;",
                    "pruefung": TABELLEN,
                    "hinweise": ["ALTER TABLE monster RENAME TO ...;  (MySQL: RENAME TABLE monster TO ...;)"],
                },
            ],
        },
        {
            "titel": "DROP, TRUNCATE & Kopien",
            "theorie": """
                # Tabellen löschen und leeren
                    DROP TABLE haendler;              -- Tabelle komplett weg (Struktur + Daten)
                    DROP TABLE IF EXISTS haendler;    -- kein Fehler, wenn es sie nicht gibt
                    TRUNCATE TABLE inventar;          -- alle Zeilen weg, Tabelle bleibt (DDL, sehr schnell)
                    DELETE FROM inventar;             -- alle Zeilen weg, Tabelle bleibt (DML, Zeile für Zeile)

                    Befehl    | Struktur | Daten | WHERE | Rollback   | AUTO_INCREMENT
                    ----------+----------+-------+-------+------------+-----------------
                    DELETE    | bleibt   | weg   | ja    | ja         | zählt weiter
                    TRUNCATE  | bleibt   | weg   | nein  | MySQL: nein| startet bei 1
                    DROP      | weg      | weg   | nein  | MySQL: nein| –

                ! SQLite kennt kein TRUNCATE – das Spiel macht daraus automatisch DELETE FROM.
                ---
                # Tabelle als Kopie anlegen
                    CREATE TABLE legendaere_items AS
                    SELECT * FROM gegenstaende WHERE seltenheit = 'Legendär';

                Erstellt eine neue Tabelle mit Struktur UND Daten aus dem SELECT.
                ? Achtung: Schlüssel und Constraints werden dabei NICHT mitkopiert.
                ! MySQL: `CREATE TABLE neu LIKE alt;` kopiert nur die Struktur (inkl. Schlüssel).
            """,
            "aufgaben": [
                {
                    "typ": "aendern",
                    "aufgabe": "Erstelle die Tabelle `legendaere_items` als Kopie aller Gegenstände mit Seltenheit 'Legendär'.",
                    "loesung": "CREATE TABLE legendaere_items AS SELECT * FROM gegenstaende WHERE seltenheit = 'Legendär';",
                    "pruefung": "SELECT * FROM legendaere_items",
                    "hinweise": ["CREATE TABLE ... AS SELECT ...", "WHERE seltenheit = 'Legendär'"],
                },
                {
                    "typ": "aendern",
                    "aufgabe": "Die Tabelle `alte_logs` wird nicht mehr gebraucht. Lösche sie komplett.",
                    "setup": "CREATE TABLE alte_logs (log_id INT, text VARCHAR(100)); INSERT INTO alte_logs VALUES (1, 'test');",
                    "loesung": "DROP TABLE alte_logs;",
                    "pruefung": TABELLEN,
                    "hinweise": ["DROP TABLE ...;"],
                },
                {
                    "typ": "aendern",
                    "aufgabe": "Leere die Tabelle `inventar` komplett – die Tabelle selbst soll erhalten bleiben. (Benutze TRUNCATE oder DELETE.)",
                    "loesung": "DELETE FROM inventar;",
                    "pruefung": [TABELLEN, "SELECT COUNT(*) FROM inventar"],
                    "hinweise": ["TRUNCATE TABLE inventar;  oder  DELETE FROM inventar;"],
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Du willst alle Zeilen löschen, deren `anzahl` = 0 ist. Was nimmst du?",
                    "optionen": ["TRUNCATE TABLE inventar WHERE anzahl = 0;",
                                 "DROP TABLE inventar WHERE anzahl = 0;",
                                 "DELETE FROM inventar WHERE anzahl = 0;",
                                 "ALTER TABLE inventar DELETE anzahl = 0;"],
                    "richtig": 3,
                    "erklaerung": "Nur DELETE kennt WHERE. TRUNCATE und DROP arbeiten immer auf der ganzen Tabelle.",
                },
            ],
        },
    ],
    "boss": {
        "titel": "Der Baumeister",
        "story": """
            # Der Baumeister fordert dich heraus!
            "Ein Turnier soll stattfinden – aber es fehlt die Tabelle!"
            Du musst MEHRERE Befehle hintereinander abgeben – jeden mit ; abschließen.
        """,
        "aufgabe": """
            1. Lege die Tabelle `turniere` an:
                 turnier_id → Ganzzahl, name → Zeichenkette bis 80 Zeichen, datum → Datum,
                 preisgeld → DECIMAL(10,2), max_teilnehmer → Ganzzahl
            2. Füge danach mit ALTER TABLE die Spalte `ort` (Zeichenkette bis 50 Zeichen) hinzu.
            3. Benenne danach die Spalte `max_teilnehmer` in `plaetze` um.
            4. Erstelle eine Kopie aller Waffen (typ = 'Waffe') aus `gegenstaende` als Tabelle `waffenkammer`.
        """,
        "loesung": """
            CREATE TABLE turniere (turnier_id INT, name VARCHAR(80), datum DATE, preisgeld DECIMAL(10,2), max_teilnehmer INT);
            ALTER TABLE turniere ADD COLUMN ort VARCHAR(50);
            ALTER TABLE turniere RENAME COLUMN max_teilnehmer TO plaetze;
            CREATE TABLE waffenkammer AS SELECT * FROM gegenstaende WHERE typ = 'Waffe';
        """,
        "typ": "aendern",
        "pruefung": [spalten("turniere"), "SELECT * FROM waffenkammer"],
        "hinweise": ["Alle vier Befehle nacheinander, jeder mit ; am Ende.", "ALTER TABLE turniere RENAME COLUMN max_teilnehmer TO plaetze;"],
    },
}
