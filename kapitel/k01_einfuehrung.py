KAPITEL = {
    "nr": 1,
    "titel": "Einführung",
    "lektionen": [
        {
            "titel": "Was ist eine Datenbank?",
            "theorie": """
                # Willkommen in der Spielwelt, Abenteurer!
                Du bist in einer RPG-Welt gelandet. Alles, was hier existiert – Spieler, Gilden,
                Monster, Gegenstände, Quests – ist in einer DATENBANK gespeichert.
                Deine Waffe: SQL. Mit jeder richtigen Abfrage sammelst du XP und steigst im Rang auf.
                ---
                # Datenbank, DBMS, RDBMS
                * Datenbank (DB): eine organisierte Sammlung von Daten.
                * DBMS (Datenbank-Management-System): die Software, die die Datenbank verwaltet
                  (speichern, suchen, Rechte, gleichzeitige Zugriffe, Absturzsicherheit).
                * RDBMS = relationales DBMS: speichert Daten in TABELLEN, die über Schlüssel
                  miteinander verbunden sind. Beispiele: MySQL, MariaDB, PostgreSQL, Oracle,
                  Microsoft SQL Server, SQLite.
                * SQL (Structured Query Language) ist die Sprache, mit der man mit einem RDBMS redet.

                ? In der Schule benutzt ihr MySQL. Dieses Spiel benutzt SQLite (ist in Python eingebaut).
                ? 95 % der Befehle sind identisch – wo es Unterschiede gibt, steht ein lila MySQL-Hinweis.
                ---
                # Tabellen, Zeilen, Spalten
                Eine Tabelle (Fachbegriff: Relation) sieht aus wie eine Excel-Tabelle:

                    spieler_id | spieler_name | klasse  | level
                    -----------+--------------+---------+------
                             1 | ShadowKnight | Krieger |    12
                             2 | PixelElf     | Magier  |    10

                * Spalte = Attribut (z.B. `klasse`). Jede Spalte hat einen festen Datentyp.
                * Zeile = Datensatz / Tupel (z.B. der Spieler ShadowKnight).
                * Zelle = ein einzelner Wert.
                * Primärschlüssel (PK) = Spalte, die jede Zeile eindeutig identifiziert (`spieler_id`).
                * Fremdschlüssel (FK) = Spalte, die auf den PK einer anderen Tabelle zeigt
                  (`spieler.gilde_id` → `gilden.gilde_id`).
                ---
                # Unsere Spielwelt (Datenbank rpg_spielwelt)
                * `gilden`        – gilde_id, gildenname, gruendungsjahr
                * `spieler`       – spieler_id, spieler_name, klasse, level, erstellt_am, gilde_id
                * `gegenstaende`  – gegenstand_id, name, typ, seltenheit, wert, beschreibung
                * `inventar`      – inventar_id, spieler_id, gegenstand_id, anzahl
                * `monster`       – monster_id, name, gebiet, stufe, ist_boss
                * `quests`        – quest_id, titel, belohnung_gold, ziel_monster_id

                Die einfachste Abfrage: alles aus einer Tabelle holen.

                    SELECT * FROM monster;

                `*` heißt "alle Spalten". Das Semikolon `;` beendet die Anweisung.
            """,
            "aufgaben": [
                {
                    "typ": "quiz",
                    "aufgabe": "Was ist ein DBMS?",
                    "optionen": ["Eine Programmiersprache für Datenbanken",
                                 "Die Software, die Datenbanken verwaltet (z.B. MySQL)",
                                 "Eine einzelne Tabelle",
                                 "Ein Dateiformat wie .csv"],
                    "richtig": 2,
                    "erklaerung": "SQL ist die Sprache, das DBMS (z.B. MySQL) ist die Software, die Datenbanken verwaltet.",
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Wie nennt man eine einzelne ZEILE in einer Tabelle?",
                    "optionen": ["Attribut", "Datensatz (Tupel)", "Relation", "Schlüssel"],
                    "richtig": 2,
                    "erklaerung": "Zeile = Datensatz/Tupel. Spalte = Attribut. Tabelle = Relation.",
                },
                {
                    "typ": "quiz",
                    "aufgabe": "In `spieler` gibt es die Spalte `gilde_id`, die auf `gilden.gilde_id` zeigt. Was ist `spieler.gilde_id`?",
                    "optionen": ["Primärschlüssel", "Fremdschlüssel", "Index", "Datentyp"],
                    "richtig": 2,
                    "erklaerung": "Ein Fremdschlüssel verweist auf den Primärschlüssel einer anderen Tabelle.",
                },
                {
                    "aufgabe": "Deine erste Abfrage! Zeige ALLE Spalten und Zeilen der Tabelle `gilden`.",
                    "loesung": "SELECT * FROM gilden;",
                    "hinweise": ["Der Stern * steht für alle Spalten.", "SELECT * FROM tabellenname;"],
                },
            ],
        },
        {
            "titel": "Die SQL-Sprachfamilien",
            "theorie": """
                # SQL besteht aus 5 Teilsprachen
                Das ist DIE Prüfungsfrage schlechthin – lern die Tabelle auswendig!

                    Kürzel | Name                         | Befehle
                    -------+------------------------------+-----------------------------------
                    DDL    | Data Definition Language     | CREATE, ALTER, DROP, TRUNCATE, RENAME
                    DML    | Data Manipulation Language   | INSERT, UPDATE, DELETE
                    DQL    | Data Query Language          | SELECT
                    DCL    | Data Control Language        | GRANT, REVOKE
                    TCL    | Transaction Control Language | COMMIT, ROLLBACK, SAVEPOINT, START TRANSACTION

                * DDL baut die STRUKTUR (Tabellen, Spalten, Indizes).
                * DML ändert die DATEN in den Tabellen.
                * DQL fragt Daten ab (manche Bücher zählen SELECT auch zur DML).
                * DCL regelt RECHTE (wer darf was).
                * TCL steuert TRANSAKTIONEN (alles-oder-nichts).

                ? Eselsbrücke: Definition = Gebäude bauen, Manipulation = Möbel umstellen,
                ? Query = durchs Fenster schauen, Control = Schlüssel verteilen, Transaction = Umzug ganz oder gar nicht.
            """,
            "aufgaben": [
                {
                    "typ": "quiz",
                    "aufgabe": "Zu welcher Teilsprache gehört `CREATE TABLE`?",
                    "optionen": ["DML", "DDL", "DCL", "TCL"],
                    "richtig": 2,
                    "erklaerung": "CREATE, ALTER, DROP verändern die Struktur → DDL.",
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Zu welcher Teilsprache gehört `UPDATE`?",
                    "optionen": ["DDL", "DQL", "DML", "DCL"],
                    "richtig": 3,
                    "erklaerung": "INSERT, UPDATE, DELETE ändern Daten → DML.",
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Mit welchem Befehl gibt man einem Benutzer Rechte – und zu welcher Teilsprache gehört er?",
                    "optionen": ["GRANT – DCL", "ALLOW – DDL", "COMMIT – TCL", "PERMIT – DML"],
                    "richtig": 1,
                    "erklaerung": "GRANT gibt Rechte, REVOKE entzieht sie. Beides DCL.",
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Was ist der Unterschied zwischen `DROP TABLE spieler` und `DELETE FROM spieler`?",
                    "optionen": ["Kein Unterschied",
                                 "DROP (DDL) löscht die ganze Tabelle samt Struktur, DELETE (DML) nur die Zeilen",
                                 "DELETE löscht die Tabelle, DROP nur die Zeilen",
                                 "DROP geht nur in MySQL"],
                    "richtig": 2,
                    "erklaerung": "Nach DELETE FROM ist die Tabelle leer, aber noch da. Nach DROP TABLE ist sie komplett weg.",
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Welcher Befehl macht alle Änderungen einer Transaktion dauerhaft?",
                    "optionen": ["SAVE", "ROLLBACK", "COMMIT", "END"],
                    "richtig": 3,
                    "erklaerung": "COMMIT bestätigt, ROLLBACK macht rückgängig. Beides TCL.",
                },
            ],
        },
        {
            "titel": "Syntax & die ersten Abfragen",
            "theorie": """
                # Grundaufbau
                    SELECT spalte1, spalte2
                    FROM tabelle;

                * Spalten werden mit Komma getrennt – NACH der letzten Spalte kommt KEIN Komma.
                * Die Reihenfolge der Spalten im SELECT bestimmt die Reihenfolge in der Ausgabe.
                * Schlüsselwörter (SELECT, FROM) sind nicht case-sensitiv: `select` = `SELECT`.
                  Konvention: Schlüsselwörter GROSS, Tabellen-/Spaltennamen klein.
                * Zeilenumbrüche und Leerzeichen sind egal – die Anweisung endet beim `;`.
                ---
                # Texte, Zahlen, Kommentare
                * Texte (Strings) immer in EINFACHEN Anführungszeichen: `'Magier'`
                  (Doppelte "..." sind in Standard-SQL für Namen von Spalten gedacht – nicht für Texte!)
                * Zahlen ohne Anführungszeichen: `12`, `3.5` (Dezimalpunkt, kein Komma!)
                * Datum als Text im Format JJJJ-MM-TT: `'2023-01-15'`
                * Ein Apostroph im Text wird verdoppelt: `'Malakor''s Turm'`

                    -- Das ist ein einzeiliger Kommentar
                    /* Das ist ein
                       mehrzeiliger Kommentar */
                    SELECT name, gebiet   -- Kommentar am Zeilenende
                    FROM monster;

                ! In MySQL braucht `--` danach ein Leerzeichen. `#` ist dort auch ein Kommentar.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige nur `spieler_name` und `klasse` aller Spieler.",
                    "loesung": "SELECT spieler_name, klasse FROM spieler;",
                    "hinweise": ["Spalten mit Komma trennen.", "SELECT spieler_name, klasse FROM ..."],
                },
                {
                    "aufgabe": "Zeige `name`, `gebiet` und `stufe` aller Monster – genau in dieser Reihenfolge.",
                    "loesung": "SELECT name, gebiet, stufe FROM monster;",
                    "hinweise": ["Die Tabelle heißt monster."],
                },
                {
                    "aufgabe": "Zeige von allen Quests den `titel` und die `belohnung_gold`. Schreib einen Kommentar mit `--` in deine Abfrage (z.B. in die Zeile davor).",
                    "loesung": "-- Alle Quests\nSELECT titel, belohnung_gold FROM quests;",
                    "hinweise": ["Mehrzeilige Eingabe geht: tipp '-- Kommentar', Enter, dann das SELECT mit ; am Ende."],
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Welche Zeile ist korrektes SQL?",
                    "optionen": ['SELECT name FROM monster WHERE gebiet = "Elchwald";',
                                 "SELECT name FROM monster WHERE gebiet = 'Elchwald';",
                                 "SELECT name, FROM monster;",
                                 "SELECT name FROM monster WHERE stufe = '3,5';"],
                    "richtig": 2,
                    "erklaerung": "Texte in einfachen Anführungszeichen. Kein Komma vor FROM. Kommazahlen mit Punkt. "
                                  "(MySQL akzeptiert zwar auch \"...\" für Texte, das ist aber kein Standard.)",
                },
            ],
        },
        {
            "titel": "Die Datenbank erkunden",
            "theorie": """
                # Wo bin ich? Welche Tabellen gibt es?
                In MySQL wählst du zuerst die Datenbank aus und schaust dich dann um:

                    USE rpg_spielwelt;     -- Datenbank auswählen
                    SHOW TABLES;           -- alle Tabellen auflisten
                    DESCRIBE spieler;      -- Spalten, Typen, Schlüssel einer Tabelle

                Das Spiel versteht diese MySQL-Befehle und übersetzt sie für SQLite.
                Zusätzlich gibt es die Spiel-Befehle `.t` (Tabellen) und `.s spieler` (Struktur + Beispielzeilen).
                ---
                # MySQL vs. SQLite – die wichtigsten Unterschiede
                * `USE`, `CREATE DATABASE` → im Spiel gibt es nur EINE Datenbank, wird ignoriert.
                * `AUTO_INCREMENT` (MySQL) heißt in SQLite `AUTOINCREMENT` – das Spiel übersetzt automatisch,
                  wenn du `id INT AUTO_INCREMENT PRIMARY KEY` schreibst.
                * `ALTER TABLE ... MODIFY` gibt es in SQLite nicht.
                * Ganzzahl-Division: `7 / 2` ergibt in SQLite `3`, in MySQL `3.5000`. Tipp: `7 / 2.0`.
                * Funktionen wie `YEAR()`, `CONCAT()`, `LEFT()`, `RIGHT()`, `DATEDIFF()`, `NOW()` funktionieren im Spiel wie in MySQL.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Liste alle Tabellen der Datenbank auf (MySQL-Befehl).",
                    "loesung": "SHOW TABLES;",
                    "hinweise": ["SHOW ..."],
                },
                {
                    "aufgabe": "Zeige die Struktur (Spalten und Typen) der Tabelle `quests` mit dem MySQL-Befehl dafür.",
                    "loesung": "DESCRIBE quests;",
                    "hinweise": ["DESCRIBE tabellenname; (Kurzform: DESC)"],
                },
                {
                    "aufgabe": "Schau dir mit `.s gegenstaende` die Tabelle an. Zeige dann `name`, `typ` und `beschreibung` aller Gegenstände.",
                    "loesung": "SELECT name, typ, beschreibung FROM gegenstaende;",
                    "hinweise": ["Die Tabelle heißt gegenstaende (ae statt ä!)."],
                },
            ],
        },
    ],
    "boss": {
        "titel": "Der Torwächter",
        "story": """
            # Der Torwächter versperrt den Weg!
            "Nur wer die Schätze dieser Welt kennt, darf passieren", grollt er.
            Er will eine Liste ALLER Gegenstände sehen – aber in seiner Reihenfolge:
            erst die Seltenheit, dann der Name, dann der Wert.
        """,
        "aufgabe": "Zeige `seltenheit`, `name` und `wert` aller Gegenstände (genau diese Spalten in genau dieser Reihenfolge).",
        "loesung": "SELECT seltenheit, name, wert FROM gegenstaende;",
        "hinweise": ["Reihenfolge im SELECT = Reihenfolge der Spalten im Ergebnis."],
    },
}
