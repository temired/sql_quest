KAPITEL = {
    "nr": 4,
    "titel": "CRUD",
    "lektionen": [
        {
            "titel": "Create – INSERT",
            "theorie": """
                # CRUD = die 4 Grundoperationen
                    C reate  →  INSERT
                    R ead    →  SELECT
                    U pdate  →  UPDATE
                    D elete  →  DELETE
                ---
                # INSERT INTO – neue Zeilen einfügen
                    INSERT INTO gilden (gildenname, gruendungsjahr)
                    VALUES ('CodeCrafters', 2026);

                * Spaltenliste und Werteliste müssen in Anzahl und Reihenfolge zusammenpassen.
                * Nicht genannte Spalten bekommen ihren DEFAULT (oder NULL). Die ID macht AUTO_INCREMENT.
                * IMMER die Spaltenliste angeben! Ohne sie (`INSERT INTO gilden VALUES (...)`) musst
                  du ALLE Spalten in Tabellenreihenfolge liefern – und alles bricht, wenn jemand eine Spalte hinzufügt.

                # Mehrere Zeilen auf einmal
                    INSERT INTO monster (name, gebiet, stufe, ist_boss) VALUES
                    ('Gargoyle', 'Turm der Verdammnis', 14, 0),
                    ('Lich', 'Verlassene Gruft', 18, 1);
                ---
                # INSERT ... SELECT – Daten aus einer Abfrage einfügen
                    INSERT INTO inventar (spieler_id, gegenstand_id, anzahl)
                    SELECT spieler_id, 14, 3
                    FROM spieler
                    WHERE klasse = 'Krieger';

                → Jeder Krieger bekommt 3 Ausdauerbrote (gegenstand_id 14). Kein VALUES!
                ? NULL explizit einfügen: einfach `NULL` schreiben (ohne Anführungszeichen).
            """,
            "aufgaben": [
                {
                    "typ": "aendern",
                    "aufgabe": "Gründe eine neue Gilde: Name 'CodeCrafters', Gründungsjahr 2026.",
                    "loesung": "INSERT INTO gilden (gildenname, gruendungsjahr) VALUES ('CodeCrafters', 2026);",
                    "pruefung": "SELECT gilde_id, gildenname, gruendungsjahr FROM gilden",
                    "hinweise": ["INSERT INTO gilden (gildenname, gruendungsjahr) VALUES (...);"],
                },
                {
                    "typ": "aendern",
                    "aufgabe": """
                        Füge mit EINEM Befehl drei Monster ein (name, gebiet, stufe, ist_boss):
                          Gargoyle – Turm der Verdammnis – 14 – 0
                          Lich – Verlassene Gruft – 18 – 1
                          Sumpfhexe – Sumpf von Sorrow – 9 – 0
                    """,
                    "loesung": """INSERT INTO monster (name, gebiet, stufe, ist_boss) VALUES
                        ('Gargoyle', 'Turm der Verdammnis', 14, 0),
                        ('Lich', 'Verlassene Gruft', 18, 1),
                        ('Sumpfhexe', 'Sumpf von Sorrow', 9, 0);""",
                    "pruefung": "SELECT monster_id, name, gebiet, stufe, ist_boss FROM monster",
                    "hinweise": ["Mehrere Wertetupel mit Komma trennen: VALUES (...), (...), (...);"],
                },
                {
                    "typ": "aendern",
                    "aufgabe": """
                        Lege dich selbst als Spieler an: Name 'SQLSchueler', Klasse 'Magier', erstellt am '2026-11-04'.
                        Gib KEIN Level und KEINE Gilde an – das Level soll der DEFAULT-Wert sein, die Gilde bleibt leer.
                    """,
                    "loesung": "INSERT INTO spieler (spieler_name, klasse, erstellt_am) VALUES ('SQLSchueler', 'Magier', '2026-11-04');",
                    "pruefung": "SELECT * FROM spieler",
                    "hinweise": ["Nur die drei Spalten spieler_name, klasse, erstellt_am in die Spaltenliste."],
                    "erklaerung": "level wurde automatisch 1 (DEFAULT), gilde_id ist NULL, spieler_id kam von AUTO_INCREMENT.",
                },
                {
                    "typ": "aendern",
                    "aufgabe": "Willkommensgeschenk: Jeder Spieler OHNE Gilde (gilde_id ist leer) bekommt 1 Heiltrank (gegenstand_id 1) ins Inventar. Benutze INSERT ... SELECT.",
                    "loesung": "INSERT INTO inventar (spieler_id, gegenstand_id, anzahl) SELECT spieler_id, 1, 1 FROM spieler WHERE gilde_id IS NULL;",
                    "pruefung": "SELECT spieler_id, gegenstand_id, anzahl FROM inventar",
                    "muss_enthalten": ["SELECT"],
                    "hinweise": ["INSERT INTO inventar (spieler_id, gegenstand_id, anzahl) SELECT ...",
                                 "Leer = NULL. Abfrage darauf: WHERE gilde_id IS NULL"],
                },
            ],
        },
        {
            "titel": "Update – UPDATE",
            "theorie": """
                # UPDATE – vorhandene Zeilen ändern
                    UPDATE spieler
                    SET level = 6
                    WHERE spieler_name = 'NoobSlayer';

                * `SET spalte = wert` – mehrere Spalten mit Komma: `SET wert = 1500, seltenheit = 'Legendär'`
                * Rechnen mit dem alten Wert: `SET level = level + 1`
                * Auf NULL setzen: `SET gilde_id = NULL`  (hier ist `=` richtig, weil es eine Zuweisung ist!)

                # ⚠ OHNE WHERE werden ALLE Zeilen geändert!
                    UPDATE spieler SET level = 1;   -- jeder Spieler ist jetzt Level 1. Viel Spaß.
                ? Profi-Tipp: Schreib zuerst ein `SELECT * FROM spieler WHERE ...` und prüfe, welche Zeilen
                ? getroffen werden. Dann erst `SELECT * FROM` durch `UPDATE ... SET ...` ersetzen.

                ! MySQL Workbench hat den "Safe Update Mode": UPDATE/DELETE ohne WHERE auf einen Schlüssel
                ! wird blockiert (Fehler 1175). Abschalten: `SET SQL_SAFE_UPDATES = 0;`
            """,
            "aufgaben": [
                {
                    "typ": "aendern",
                    "aufgabe": "NoobSlayer ist aufgestiegen: Setze sein Level auf 6.",
                    "loesung": "UPDATE spieler SET level = 6 WHERE spieler_name = 'NoobSlayer';",
                    "pruefung": "SELECT spieler_name, level FROM spieler",
                    "hinweise": ["UPDATE spieler SET level = ... WHERE spieler_name = '...';"],
                },
                {
                    "typ": "aendern",
                    "aufgabe": "Kriegerfest! Alle Spieler der Klasse 'Krieger' steigen um 1 Level auf.",
                    "loesung": "UPDATE spieler SET level = level + 1 WHERE klasse = 'Krieger';",
                    "pruefung": "SELECT spieler_name, level FROM spieler",
                    "hinweise": ["SET level = level + 1"],
                },
                {
                    "typ": "aendern",
                    "aufgabe": "Das Flammenschwert wurde verbessert: wert = 1500 und seltenheit = 'Legendär' (beides in einem UPDATE).",
                    "loesung": "UPDATE gegenstaende SET wert = 1500, seltenheit = 'Legendär' WHERE name = 'Flammenschwert';",
                    "pruefung": "SELECT name, wert, seltenheit FROM gegenstaende",
                    "hinweise": ["SET spalte1 = ..., spalte2 = ..."],
                },
                {
                    "typ": "aendern",
                    "aufgabe": "Sale im Trankladen: Alle Gegenstände vom typ 'Trank' werden 20 % billiger. Runde auf ganze Zahlen (ROUND).",
                    "loesung": "UPDATE gegenstaende SET wert = ROUND(wert * 0.8) WHERE typ = 'Trank';",
                    "auch_richtig": ["UPDATE gegenstaende SET wert = ROUND(wert * 0.80, 0) WHERE typ = 'Trank';"],
                    "pruefung": "SELECT name, wert FROM gegenstaende",
                    "hinweise": ["20 % billiger = wert * 0.8", "ROUND(wert * 0.8)"],
                },
                {
                    "typ": "aendern",
                    "aufgabe": "ShadowKnight verlässt seine Gilde. Setze seine gilde_id auf NULL.",
                    "loesung": "UPDATE spieler SET gilde_id = NULL WHERE spieler_name = 'ShadowKnight';",
                    "pruefung": "SELECT spieler_name, gilde_id FROM spieler",
                    "hinweise": ["SET gilde_id = NULL"],
                },
            ],
        },
        {
            "titel": "Delete – DELETE",
            "theorie": """
                # DELETE – Zeilen löschen
                    DELETE FROM quests
                    WHERE quest_id = 15;

                * Es werden ganze ZEILEN gelöscht – einzelne Werte "löscht" man mit `UPDATE ... SET x = NULL`.
                * ⚠ `DELETE FROM quests;` ohne WHERE löscht ALLE Quests!
                * Fremdschlüssel schützen dich: Eine Zeile, auf die noch andere zeigen, kann nicht
                  gelöscht werden (außer ON DELETE CASCADE / SET NULL ist eingestellt).
                  → Erst die Kinder löschen, dann die Eltern.

                ! Euer Lehrer hat in 10_Delete.sql `SET FOREIGN_KEY_CHECKS = 0;` benutzt, um das zu umgehen.
                ! Das geht, hinterlässt aber verwaiste Datensätze (Quests, deren Monster es nicht mehr gibt)!
            """,
            "aufgaben": [
                {
                    "typ": "aendern",
                    "aufgabe": "Lösche die Quest mit dem Titel 'Kräuter sammeln'.",
                    "loesung": "DELETE FROM quests WHERE titel = 'Kräuter sammeln';",
                    "pruefung": "SELECT titel FROM quests",
                    "hinweise": ["DELETE FROM quests WHERE titel = '...';"],
                },
                {
                    "typ": "aendern",
                    "aufgabe": "Lösche aus dem Inventar alle Einträge von Spieler 3, bei denen die anzahl genau 1 ist.",
                    "loesung": "DELETE FROM inventar WHERE spieler_id = 3 AND anzahl = 1;",
                    "pruefung": "SELECT inventar_id, spieler_id, anzahl FROM inventar",
                    "hinweise": ["Zwei Bedingungen mit AND verknüpfen."],
                },
                {
                    "typ": "aendern",
                    "aufgabe": """
                        Das Monster 'Schleim' soll aus dem Spiel verschwinden. Es wird aber noch von einer Quest
                        referenziert (ziel_monster_id = 4). Lösche zuerst die Quest(s), die auf den Schleim zeigen,
                        und dann den Schleim selbst. (Zwei DELETE-Befehle, FOREIGN_KEY_CHECKS bleibt an!)
                    """,
                    "loesung": "DELETE FROM quests WHERE ziel_monster_id = 4;\nDELETE FROM monster WHERE name = 'Schleim';",
                    "pruefung": ["SELECT name FROM monster", "SELECT titel FROM quests"],
                    "hinweise": ["DELETE FROM quests WHERE ziel_monster_id = 4;", "Danach: DELETE FROM monster WHERE name = 'Schleim';"],
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Was macht `DELETE FROM spieler;`?",
                    "optionen": ["Fehler, weil WHERE fehlt",
                                 "Löscht die Tabelle spieler",
                                 "Löscht ALLE Zeilen aus spieler (soweit Fremdschlüssel es erlauben)",
                                 "Löscht nur die erste Zeile"],
                    "richtig": 3,
                },
            ],
        },
        {
            "titel": "Transaktionen",
            "theorie": """
                # Alles oder nichts
                Spieler A überweist 30 Gold an Spieler B. Das sind ZWEI Updates:
                    UPDATE spieler SET gold = gold - 30 WHERE spieler_name = 'A';
                    UPDATE spieler SET gold = gold + 30 WHERE spieler_name = 'B';
                Stürzt der Server zwischen den beiden ab, ist das Gold verschwunden!
                Eine TRANSAKTION fasst mehrere Befehle zu einer unteilbaren Einheit zusammen:

                    START TRANSACTION;          -- (SQLite: BEGIN;)
                    UPDATE ... ;
                    UPDATE ... ;
                    COMMIT;                     -- alles dauerhaft speichern
                    -- oder ROLLBACK;           -- alles seit START TRANSACTION rückgängig machen
                ---
                # ACID – die 4 Garantien einer Transaktion (Prüfungsklassiker!)
                * A – Atomicity (Atomarität): ganz oder gar nicht.
                * C – Consistency (Konsistenz): danach gelten wieder alle Regeln/Constraints.
                * I – Isolation: parallele Transaktionen stören sich nicht gegenseitig.
                * D – Durability (Dauerhaftigkeit): nach COMMIT überlebt es auch einen Absturz.

                # Weitere Befehle
                    SAVEPOINT vor_dem_kauf;          -- Zwischenstand merken
                    ROLLBACK TO vor_dem_kauf;        -- nur bis dahin zurück
                ! MySQL läuft standardmäßig im AUTOCOMMIT-Modus: jede einzelne Anweisung wird sofort committet,
                ! außer du startest explizit eine Transaktion. DDL (CREATE, DROP...) committet in MySQL immer sofort!
                ---
                # UPSERT – einfügen ODER aktualisieren
                Gibt es den Datensatz schon, soll er aktualisiert werden, sonst neu angelegt:
                    -- MySQL
                    INSERT INTO inventar (inventar_id, spieler_id, gegenstand_id, anzahl)
                    VALUES (1, 1, 1, 5)
                    ON DUPLICATE KEY UPDATE anzahl = anzahl + 5;

                    -- SQLite / PostgreSQL
                    INSERT INTO ... VALUES (...)
                    ON CONFLICT (inventar_id) DO UPDATE SET anzahl = anzahl + 5;
                ! `REPLACE INTO` (MySQL) löscht die alte Zeile und fügt neu ein – Vorsicht bei Fremdschlüsseln.
            """,
            "aufgaben": [
                {
                    "typ": "aendern",
                    "setup": "ALTER TABLE spieler ADD COLUMN gold INT NOT NULL DEFAULT 100 CHECK (gold >= 0);",
                    "aufgabe": """
                        Jeder Spieler hat jetzt eine Spalte `gold` (Start: 100).
                        ShadowKnight überweist 30 Gold an PixelElf. Mach das sauber in einer Transaktion:
                        START TRANSACTION (oder BEGIN), zwei UPDATEs, COMMIT.
                    """,
                    "loesung": """START TRANSACTION;
                        UPDATE spieler SET gold = gold - 30 WHERE spieler_name = 'ShadowKnight';
                        UPDATE spieler SET gold = gold + 30 WHERE spieler_name = 'PixelElf';
                        COMMIT;""",
                    "pruefung": "SELECT spieler_name, gold FROM spieler",
                    "muss_enthalten": ["COMMIT"],
                    "hinweise": ["START TRANSACTION; UPDATE ...; UPDATE ...; COMMIT;"],
                },
                {
                    "typ": "aendern",
                    "setup": "ALTER TABLE spieler ADD COLUMN gold INT NOT NULL DEFAULT 100;",
                    "aufgabe": """
                        Ups-Test: Starte eine Transaktion und lösche ALLE Zeilen aus `inventar`.
                        Schau mit SELECT COUNT(*) FROM inventar; nach (0!). Mach dann alles mit ROLLBACK rückgängig.
                        Gib danach (außerhalb der Transaktion) FireMage 50 Gold dazu.
                    """,
                    "loesung": """BEGIN;
                        DELETE FROM inventar;
                        SELECT COUNT(*) FROM inventar;
                        ROLLBACK;
                        UPDATE spieler SET gold = gold + 50 WHERE spieler_name = 'FireMage';""",
                    "pruefung": ["SELECT COUNT(*) AS inventar_zeilen FROM inventar", "SELECT spieler_name, gold FROM spieler"],
                    "muss_enthalten": ["ROLLBACK"],
                    "hinweise": ["BEGIN; DELETE FROM inventar; ROLLBACK;", "Danach normal: UPDATE spieler SET gold = gold + 50 WHERE ..."],
                    "erklaerung": "Nach dem ROLLBACK war das Inventar wieder vollständig da – als wäre nichts passiert.",
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Wofür steht das 'A' in ACID?",
                    "optionen": ["Availability – die DB ist immer erreichbar",
                                 "Atomicity – eine Transaktion wird ganz oder gar nicht ausgeführt",
                                 "Authentication – nur angemeldete Nutzer",
                                 "Aggregation – Daten werden zusammengefasst"],
                    "richtig": 2,
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Eine Transaktion führt 2 UPDATEs aus, das zweite verletzt einen CHECK-Constraint. Das Programm führt danach ROLLBACK aus. Was ist der Zustand?",
                    "optionen": ["Das erste UPDATE bleibt bestehen",
                                 "Beide UPDATEs sind rückgängig gemacht",
                                 "Beide UPDATEs sind gespeichert",
                                 "Die Tabelle ist gelöscht"],
                    "richtig": 2,
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Welches 'I' aus ACID sorgt dafür, dass zwei gleichzeitige Überweisungen sich nicht gegenseitig in die Quere kommen?",
                    "optionen": ["Integrity", "Isolation", "Index", "Immutability"],
                    "richtig": 2,
                },
            ],
        },
    ],
    "boss": {
        "titel": "Die große Gildenreform",
        "story": """
            # Der König verlangt eine Gildenreform!
            Mehrere Anweisungen hintereinander, jede mit ; abgeschlossen.
            (Im Terminal-Modus geht das bequem über die Datei antwort.sql und .d)
        """,
        "typ": "aendern",
        "aufgabe": """
            1. Gründe die Gilde 'PhoenixReborn' (Gründungsjahr 2026). Sie bekommt die gilde_id 16.
            2. Alle Spieler ohne Gilde treten 'PhoenixReborn' bei.
            3. Alle Mitglieder von 'PhoenixReborn' steigen um 2 Level auf.
            4. Die Gilde 'DoomSlayers' wird aufgelöst (gelöscht).
            5. Die Quest 'Kräuter sammeln' bekommt das Zielmonster 'Goblin' (monster_id 1) und 50 Gold Belohnung.
        """,
        "loesung": """
            INSERT INTO gilden (gildenname, gruendungsjahr) VALUES ('PhoenixReborn', 2026);
            UPDATE spieler SET gilde_id = 16 WHERE gilde_id IS NULL;
            UPDATE spieler SET level = level + 2 WHERE gilde_id = 16;
            DELETE FROM gilden WHERE gildenname = 'DoomSlayers';
            UPDATE quests SET ziel_monster_id = 1, belohnung_gold = 50 WHERE titel = 'Kräuter sammeln';
        """,
        "pruefung": ["SELECT gilde_id, gildenname, gruendungsjahr FROM gilden",
                     "SELECT spieler_name, level, gilde_id FROM spieler",
                     "SELECT titel, belohnung_gold, ziel_monster_id FROM quests"],
        "hinweise": ["Spieler ohne Gilde: WHERE gilde_id IS NULL",
                     "Erst den Beitritt (gilde_id = 16), dann das Level-Update auf gilde_id = 16."],
    },
}
