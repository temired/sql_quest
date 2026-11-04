from ._hilfe import spaltennamen

KAPITEL = {
    "nr": 3,
    "titel": "Constraints",
    "lektionen": [
        {
            "titel": "PRIMARY KEY & AUTO_INCREMENT",
            "theorie": """
                # Constraints = Regeln, die die Datenbank erzwingt
                Ohne Regeln landet Müll in der Datenbank (doppelte IDs, leere Namen, Level -5 ...).
                Constraints werden beim CREATE TABLE festgelegt und bei JEDEM Insert/Update geprüft.

                    Constraint   | Bedeutung
                    -------------+----------------------------------------------------
                    PRIMARY KEY  | eindeutig + nicht NULL, identifiziert jede Zeile
                    NOT NULL     | Pflichtfeld
                    UNIQUE       | kein Wert doppelt (NULL ist aber erlaubt)
                    DEFAULT      | Standardwert, wenn nichts angegeben wird
                    CHECK        | Bedingung muss erfüllt sein
                    FOREIGN KEY  | Wert muss in einer anderen Tabelle existieren
                ---
                # PRIMARY KEY (Primärschlüssel)
                    CREATE TABLE haendler (
                        haendler_id  INT PRIMARY KEY,
                        name         VARCHAR(50)
                    );

                * Jede Tabelle sollte GENAU EINEN Primärschlüssel haben.
                * Er darf nie doppelt und nie NULL sein.
                * Surrogatschlüssel = künstliche ID ohne Bedeutung (`haendler_id`) – der Normalfall.
                * Natürlicher Schlüssel = echter Wert, der eindeutig ist (ISBN, Steuer-ID).
                ---
                # AUTO_INCREMENT – IDs automatisch vergeben
                    CREATE TABLE schmiede (
                        schmiede_id  INT AUTO_INCREMENT PRIMARY KEY,   -- MySQL
                        ort          VARCHAR(50)
                    );
                    INSERT INTO schmiede (ort) VALUES ('Eisenfels');   -- bekommt id 1
                    INSERT INTO schmiede (ort) VALUES ('Glutheim');    -- bekommt id 2

                ! In SQLite heißt es `schmiede_id INTEGER PRIMARY KEY AUTOINCREMENT`.
                ! Das Spiel versteht auch die MySQL-Schreibweise und übersetzt sie.
                ---
                # Zusammengesetzter Primärschlüssel
                Manchmal ist erst die KOMBINATION mehrerer Spalten eindeutig:
                Ein Spieler kann viele Quests haben, eine Quest viele Spieler – aber jede
                Kombination (Spieler, Quest) gibt es nur einmal.

                    CREATE TABLE quest_fortschritt (
                        spieler_id  INT,
                        quest_id    INT,
                        status      VARCHAR(20),
                        PRIMARY KEY (spieler_id, quest_id)
                    );

                Der PK steht dann als eigene Zeile am Ende (Tabellen-Constraint).
            """,
            "aufgaben": [
                {
                    "typ": "aendern",
                    "aufgabe": "Lege `haendler` an: `haendler_id` (Ganzzahl, Primärschlüssel) und `name` (Zeichenkette bis 50 Zeichen).",
                    "loesung": "CREATE TABLE haendler (haendler_id INT PRIMARY KEY, name VARCHAR(50));",
                    "pruefung": spaltennamen("haendler"),
                    "tests": ["INSERT INTO haendler VALUES (1, 'Gorm')",
                              "INSERT INTO haendler VALUES (2, 'Lyra')",
                              "INSERT INTO haendler VALUES (1, 'Doppelgänger')"],
                    "hinweise": ["haendler_id INT PRIMARY KEY"],
                },
                {
                    "typ": "aendern",
                    "aufgabe": """
                        Lege `schmiede` an: `schmiede_id` (Primärschlüssel, wird AUTOMATISCH hochgezählt)
                        und `ort` (Zeichenkette bis 50 Zeichen). Getestet wird mit INSERTs, die nur den Ort angeben.
                    """,
                    "loesung": "CREATE TABLE schmiede (schmiede_id INTEGER PRIMARY KEY AUTOINCREMENT, ort VARCHAR(50));",
                    "auch_richtig": ["CREATE TABLE schmiede (schmiede_id INT AUTO_INCREMENT PRIMARY KEY, ort VARCHAR(50));",
                                     "CREATE TABLE schmiede (schmiede_id INT NOT NULL AUTO_INCREMENT, ort VARCHAR(50), PRIMARY KEY (schmiede_id));"],
                    "tests": ["INSERT INTO schmiede (ort) VALUES ('Eisenfels')", "INSERT INTO schmiede (ort) VALUES ('Glutheim')"],
                    "pruefung": "SELECT schmiede_id, ort FROM schmiede ORDER BY ort",
                    "hinweise": ["MySQL: schmiede_id INT AUTO_INCREMENT PRIMARY KEY", "SQLite: schmiede_id INTEGER PRIMARY KEY AUTOINCREMENT"],
                },
                {
                    "typ": "aendern",
                    "aufgabe": """
                        Lege `quest_fortschritt` an: `spieler_id` (Ganzzahl), `quest_id` (Ganzzahl), `status` (Zeichenkette bis 20 Zeichen).
                        Die KOMBINATION aus spieler_id und quest_id soll der Primärschlüssel sein.
                    """,
                    "loesung": "CREATE TABLE quest_fortschritt (spieler_id INT, quest_id INT, status VARCHAR(20), PRIMARY KEY (spieler_id, quest_id));",
                    "pruefung": spaltennamen("quest_fortschritt"),
                    "tests": ["INSERT INTO quest_fortschritt VALUES (1, 1, 'offen')",
                              "INSERT INTO quest_fortschritt VALUES (1, 2, 'offen')",
                              "INSERT INTO quest_fortschritt VALUES (2, 1, 'fertig')",
                              "INSERT INTO quest_fortschritt VALUES (1, 1, 'fertig')"],
                    "hinweise": ["Am Ende der Spaltenliste: PRIMARY KEY (spalte1, spalte2)"],
                },
            ],
        },
        {
            "titel": "NOT NULL, DEFAULT, UNIQUE",
            "theorie": """
                # NOT NULL – Pflichtfelder
                NULL bedeutet "kein Wert / unbekannt" (nicht 0, nicht leerer Text!).
                    name VARCHAR(50) NOT NULL

                # DEFAULT – Standardwert
                    rolle  VARCHAR(20) DEFAULT 'spieler',
                    gold   INT NOT NULL DEFAULT 0,
                    erstellt_am DATETIME DEFAULT CURRENT_TIMESTAMP
                Gibt man beim INSERT die Spalte nicht an, wird der DEFAULT eingesetzt.

                # UNIQUE – keine Duplikate
                    email VARCHAR(255) NOT NULL UNIQUE
                * Unterschied zum PK: Es darf mehrere UNIQUE-Spalten geben, und UNIQUE erlaubt NULL.
                * UNIQUE über mehrere Spalten: `UNIQUE (vorname, nachname)` als eigene Zeile.

                # Constraints benennen (gute Praxis, Fehlermeldungen werden lesbarer)
                    CONSTRAINT uq_accounts_email UNIQUE (email)
            """,
            "aufgaben": [
                {
                    "typ": "aendern",
                    "aufgabe": """
                        Lege `accounts` an:
                          account_id     → Primärschlüssel, automatisch hochzählend
                          email          → Zeichenkette bis 255 Zeichen, Pflichtfeld, darf nicht doppelt vorkommen
                          passwort_hash  → Zeichenkette bis 255 Zeichen, Pflichtfeld
                          rolle          → Zeichenkette bis 20 Zeichen, Standardwert 'spieler'
                    """,
                    "loesung": """CREATE TABLE accounts (
                        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email VARCHAR(255) NOT NULL UNIQUE,
                        passwort_hash VARCHAR(255) NOT NULL,
                        rolle VARCHAR(20) DEFAULT 'spieler');""",
                    "tests": ["INSERT INTO accounts (email, passwort_hash) VALUES ('a@quest.de', 'x1')",
                              "INSERT INTO accounts (email, passwort_hash, rolle) VALUES ('b@quest.de', 'x2', 'admin')",
                              "INSERT INTO accounts (email, passwort_hash) VALUES ('a@quest.de', 'x3')",
                              "INSERT INTO accounts (email, passwort_hash) VALUES (NULL, 'x4')",
                              "INSERT INTO accounts (email) VALUES ('c@quest.de')"],
                    "pruefung": "SELECT account_id, email, rolle FROM accounts ORDER BY account_id",
                    "hinweise": ["email VARCHAR(255) NOT NULL UNIQUE", "rolle VARCHAR(20) DEFAULT 'spieler'"],
                },
                {
                    "typ": "aendern",
                    "aufgabe": """
                        Lege `charaktere` an: `char_id` (Primärschlüssel, automatisch), `vorname` (Zeichenkette bis 30 Zeichen, Pflicht),
                        `nachname` (Zeichenkette bis 30 Zeichen, Pflicht), `level` (Ganzzahl, Pflicht, Standard 1).
                        Die Kombination aus vorname + nachname darf nur EINMAL vorkommen.
                    """,
                    "loesung": """CREATE TABLE charaktere (
                        char_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        vorname VARCHAR(30) NOT NULL,
                        nachname VARCHAR(30) NOT NULL,
                        level INT NOT NULL DEFAULT 1,
                        UNIQUE (vorname, nachname));""",
                    "tests": ["INSERT INTO charaktere (vorname, nachname) VALUES ('Aria', 'Sturm')",
                              "INSERT INTO charaktere (vorname, nachname) VALUES ('Aria', 'Stein')",
                              "INSERT INTO charaktere (vorname, nachname) VALUES ('Bran', 'Sturm')",
                              "INSERT INTO charaktere (vorname, nachname) VALUES ('Aria', 'Sturm')",
                              "INSERT INTO charaktere (vorname, nachname, level) VALUES ('Cid', NULL, 5)",
                              "INSERT INTO charaktere (vorname, nachname, level) VALUES ('Dax', 'Eis', NULL)"],
                    "pruefung": "SELECT vorname, nachname, level FROM charaktere ORDER BY char_id",
                    "hinweise": ["UNIQUE (vorname, nachname) als eigene Zeile am Ende", "level INT NOT NULL DEFAULT 1"],
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Was ist der Unterschied zwischen PRIMARY KEY und UNIQUE?",
                    "optionen": ["Es gibt keinen",
                                 "PK: genau einer pro Tabelle und nie NULL. UNIQUE: mehrere erlaubt, NULL erlaubt",
                                 "UNIQUE ist schneller",
                                 "PK darf doppelt sein, UNIQUE nicht"],
                    "richtig": 2,
                },
            ],
        },
        {
            "titel": "CHECK",
            "theorie": """
                # CHECK – Wertebereich erzwingen
                    CREATE TABLE auktionen (
                        auktion_id     INTEGER PRIMARY KEY,
                        startpreis     INT CHECK (startpreis > 0),
                        dauer_stunden  INT CHECK (dauer_stunden BETWEEN 1 AND 72),
                        status         VARCHAR(10) CHECK (status IN ('offen', 'verkauft', 'abgelaufen'))
                    );

                * Die Bedingung ist wie ein WHERE: `>`, `BETWEEN`, `IN (...)`, `AND`/`OR` ...
                * Beziehen sich mehrere Spalten aufeinander, schreibt man den CHECK ans Ende:
                    `CHECK (endpreis >= startpreis)`
                * Unsere `spieler`-Tabelle hat übrigens `CHECK (level BETWEEN 1 AND 100)`.

                ! MySQL beachtet CHECK erst ab Version 8.0.16 – vorher wurde CHECK stillschweigend ignoriert!
                ! Statt `IN (...)` nimmt man in MySQL oft `ENUM('offen','verkauft','abgelaufen')`.
            """,
            "aufgaben": [
                {
                    "typ": "aendern",
                    "aufgabe": """
                        Lege `auktionen` an:
                          auktion_id     → Primärschlüssel (Ganzzahl)
                          gegenstand     → Zeichenkette bis 50 Zeichen, Pflichtfeld
                          startpreis     → Ganzzahl, muss größer als 0 sein
                          dauer_stunden  → Ganzzahl, nur 1 bis 72 erlaubt
                    """,
                    "loesung": """CREATE TABLE auktionen (
                        auktion_id INT PRIMARY KEY,
                        gegenstand VARCHAR(50) NOT NULL,
                        startpreis INT CHECK (startpreis > 0),
                        dauer_stunden INT CHECK (dauer_stunden BETWEEN 1 AND 72));""",
                    "tests": ["INSERT INTO auktionen VALUES (1, 'Heiltrank', 10, 24)",
                              "INSERT INTO auktionen VALUES (2, 'Manatrank', 0, 24)",
                              "INSERT INTO auktionen VALUES (3, 'Manatrank', -5, 24)",
                              "INSERT INTO auktionen VALUES (4, 'Eisenhelm', 100, 72)",
                              "INSERT INTO auktionen VALUES (5, 'Eisenhelm', 100, 73)",
                              "INSERT INTO auktionen VALUES (6, 'Eisenhelm', 100, 0)",
                              "INSERT INTO auktionen VALUES (7, NULL, 100, 10)"],
                    "pruefung": "SELECT * FROM auktionen ORDER BY auktion_id",
                    "hinweise": ["startpreis INT CHECK (startpreis > 0)", "CHECK (dauer_stunden BETWEEN 1 AND 72)"],
                },
                {
                    "typ": "aendern",
                    "aufgabe": """
                        Lege `reittiere` an: `tier_id` (Primärschlüssel, Ganzzahl), `name` (Zeichenkette bis 30 Zeichen),
                        `art` (Zeichenkette bis 20 Zeichen) – erlaubt sind NUR 'Pferd', 'Greif' und 'Drache',
                        `geschwindigkeit` (Ganzzahl) und `max_geschwindigkeit` (Ganzzahl).
                        Zusätzlich: geschwindigkeit darf nie größer als max_geschwindigkeit sein.
                    """,
                    "loesung": """CREATE TABLE reittiere (
                        tier_id INT PRIMARY KEY, name VARCHAR(30),
                        art VARCHAR(20) CHECK (art IN ('Pferd', 'Greif', 'Drache')),
                        geschwindigkeit INT, max_geschwindigkeit INT,
                        CHECK (geschwindigkeit <= max_geschwindigkeit));""",
                    "auch_richtig": ["""CREATE TABLE reittiere (tier_id INT PRIMARY KEY, name VARCHAR(30),
                        art ENUM('Pferd','Greif','Drache'), geschwindigkeit INT, max_geschwindigkeit INT,
                        CHECK (geschwindigkeit <= max_geschwindigkeit));"""],
                    "tests": ["INSERT INTO reittiere VALUES (1, 'Blitz', 'Pferd', 50, 60)",
                              "INSERT INTO reittiere VALUES (2, 'Flausch', 'Einhorn', 50, 60)",
                              "INSERT INTO reittiere VALUES (3, 'Glut', 'Drache', 90, 80)",
                              "INSERT INTO reittiere VALUES (4, 'Wolke', 'Greif', 80, 80)"],
                    "pruefung": "SELECT * FROM reittiere ORDER BY tier_id",
                    "hinweise": ["art VARCHAR(20) CHECK (art IN ('Pferd', 'Greif', 'Drache'))",
                                 "Am Ende: CHECK (geschwindigkeit <= max_geschwindigkeit)"],
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Die Tabelle `spieler` hat CHECK (level BETWEEN 1 AND 100). Was passiert bei `UPDATE spieler SET level = 150 WHERE spieler_id = 1;`? (Danach gern in der Sandbox ausprobieren!)",
                    "optionen": ["Level wird auf 150 gesetzt",
                                 "Level wird automatisch auf 100 begrenzt",
                                 "Fehler – das UPDATE wird abgelehnt, nichts ändert sich",
                                 "Der Spieler wird gelöscht"],
                    "richtig": 3,
                    "erklaerung": "Constraints lehnen die ganze Anweisung ab. Es wird nichts 'zurechtgebogen'.",
                },
            ],
        },
        {
            "titel": "FOREIGN KEY",
            "theorie": """
                # Fremdschlüssel – Beziehungen absichern
                `spieler.gilde_id` zeigt auf `gilden.gilde_id`. Ohne FOREIGN KEY könnte jemand
                `gilde_id = 999` eintragen, obwohl es Gilde 999 nicht gibt → kaputte Daten.
                Das nennt man referentielle Integrität.

                    CREATE TABLE angebote (
                        angebot_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                        haendler_id   INT NOT NULL,
                        gegenstand_id INT NOT NULL,
                        preis         INT,
                        FOREIGN KEY (haendler_id) REFERENCES haendler(haendler_id),
                        FOREIGN KEY (gegenstand_id) REFERENCES gegenstaende(gegenstand_id)
                    );

                Kurzform direkt an der Spalte:
                    haendler_id INT NOT NULL REFERENCES haendler(haendler_id)
                ---
                # Was passiert beim Löschen des "Elternteils"?
                    ... REFERENCES spieler(spieler_id) ON DELETE CASCADE

                    Option            | Wird der Elterndatensatz gelöscht, dann ...
                    ------------------+----------------------------------------------
                    RESTRICT/NO ACTION| ... wird das Löschen VERWEIGERT (Standard)
                    CASCADE           | ... werden die Kind-Zeilen MIT gelöscht
                    SET NULL          | ... wird der Fremdschlüssel auf NULL gesetzt
                    SET DEFAULT       | ... wird der Standardwert eingesetzt

                Genauso gibt es `ON UPDATE CASCADE` (wenn sich der PK ändert).
                In unserer Welt: `inventar` → spieler ON DELETE CASCADE, `spieler` → gilden ON DELETE SET NULL.

                ! MySQL: Foreign Keys gehen nur mit der Engine InnoDB (Standard). Mit
                ! `SET FOREIGN_KEY_CHECKS = 0;` kann man sie kurz abschalten (wie euer Lehrer in 10_Delete.sql).
                ! Fremdschlüssel nachträglich: `ALTER TABLE x ADD CONSTRAINT fk_name FOREIGN KEY (...) REFERENCES ...;`
                ! (in SQLite nicht möglich – hier immer direkt im CREATE TABLE).
            """,
            "aufgaben": [
                {
                    "typ": "aendern",
                    "setup": "CREATE TABLE haendler (haendler_id INTEGER PRIMARY KEY, name VARCHAR(50)); INSERT INTO haendler VALUES (1, 'Gorm'), (2, 'Lyra');",
                    "aufgabe": """
                        Die Tabelle `haendler` existiert schon. Lege `angebote` an:
                          angebot_id    → Primärschlüssel, automatisch
                          haendler_id   → Pflicht, Fremdschlüssel auf haendler(haendler_id)
                          gegenstand_id → Pflicht, Fremdschlüssel auf gegenstaende(gegenstand_id)
                          preis         → Ganzzahl
                    """,
                    "loesung": """CREATE TABLE angebote (
                        angebot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        haendler_id INT NOT NULL,
                        gegenstand_id INT NOT NULL,
                        preis INT,
                        FOREIGN KEY (haendler_id) REFERENCES haendler(haendler_id),
                        FOREIGN KEY (gegenstand_id) REFERENCES gegenstaende(gegenstand_id));""",
                    "tests": ["INSERT INTO angebote (haendler_id, gegenstand_id, preis) VALUES (1, 1, 55)",
                              "INSERT INTO angebote (haendler_id, gegenstand_id, preis) VALUES (2, 5, 4000)",
                              "INSERT INTO angebote (haendler_id, gegenstand_id, preis) VALUES (99, 1, 10)",
                              "INSERT INTO angebote (haendler_id, gegenstand_id, preis) VALUES (1, 999, 10)",
                              "INSERT INTO angebote (haendler_id, gegenstand_id, preis) VALUES (NULL, 1, 10)"],
                    "pruefung": "SELECT haendler_id, gegenstand_id, preis FROM angebote ORDER BY angebot_id",
                    "hinweise": ["FOREIGN KEY (haendler_id) REFERENCES haendler(haendler_id)"],
                },
                {
                    "typ": "aendern",
                    "aufgabe": """
                        Lege `erfolge` an: `erfolg_id` (Primärschlüssel, Ganzzahl), `spieler_id` (Fremdschlüssel auf spieler),
                        `titel` (Zeichenkette bis 50 Zeichen). Wird ein Spieler gelöscht, sollen seine Erfolge AUTOMATISCH mitgelöscht werden.
                    """,
                    "loesung": """CREATE TABLE erfolge (
                        erfolg_id INT PRIMARY KEY,
                        spieler_id INT REFERENCES spieler(spieler_id) ON DELETE CASCADE,
                        titel VARCHAR(50));""",
                    "tests": ["INSERT INTO erfolge VALUES (1, 1, 'Erster Sieg')",
                              "INSERT INTO erfolge VALUES (2, 2, 'Feuerteufel')",
                              "INSERT INTO erfolge VALUES (3, 1, 'Drachentöter')",
                              "INSERT INTO erfolge VALUES (4, 500, 'Geist')",
                              "DELETE FROM spieler WHERE spieler_id = 1"],
                    "pruefung": "SELECT * FROM erfolge ORDER BY erfolg_id",
                    "hinweise": ["... REFERENCES spieler(spieler_id) ON DELETE CASCADE"],
                },
                {
                    "typ": "aendern",
                    "aufgabe": """
                        Probier die Regel aus! `spieler.gilde_id` hat ON DELETE SET NULL.
                        Lösche die Gilde 'DragonSlayers' aus `gilden` – und schau danach mit SELECT nach,
                        was mit ShadowKnight und NoobSlayer passiert ist.
                    """,
                    "loesung": "DELETE FROM gilden WHERE gildenname = 'DragonSlayers';",
                    "pruefung": ["SELECT gildenname FROM gilden", "SELECT spieler_name, gilde_id FROM spieler"],
                    "hinweise": ["DELETE FROM gilden WHERE gildenname = '...';"],
                    "erklaerung": "Die Spieler existieren weiter, aber ihre gilde_id ist jetzt NULL (gildenlos).",
                },
                {
                    "typ": "quiz",
                    "aufgabe": "`quests.ziel_monster_id` verweist ohne ON DELETE-Regel auf `monster`. Was passiert bei `DELETE FROM monster WHERE name = 'Goblin';`?",
                    "optionen": ["Goblin wird gelöscht, die Quest auch",
                                 "Goblin wird gelöscht, die Quest bekommt NULL",
                                 "Fehler: FOREIGN KEY constraint failed – Goblin wird noch von einer Quest referenziert",
                                 "Goblin wird gelöscht, die Quest zeigt ins Leere"],
                    "richtig": 3,
                    "erklaerung": "Ohne Regel gilt RESTRICT/NO ACTION. Erst die Quest löschen (oder umhängen), dann das Monster.",
                },
            ],
        },
    ],
    "boss": {
        "titel": "Der Auktionator",
        "story": """
            # Der Auktionator will ein fälschungssicheres Bietersystem!
            Die Tabelle `auktionen` existiert schon (auktion_id, gegenstand, startpreis).
            Baue die Tabelle für die Gebote – mit ALLEN Regeln. Jede Regel wird getestet.
        """,
        "setup": """CREATE TABLE auktionen (auktion_id INTEGER PRIMARY KEY, gegenstand VARCHAR(50), startpreis INT);
                    INSERT INTO auktionen VALUES (1, 'Drachenbogen', 3000), (2, 'Heiltrank', 20);""",
        "typ": "aendern",
        "aufgabe": """
            Lege `gebote` an:
              gebot_id    → Primärschlüssel, automatisch hochzählend
              auktion_id  → Pflicht, Fremdschlüssel auf auktionen; wird die Auktion gelöscht, verschwinden ihre Gebote mit
              spieler_id  → Pflicht, Fremdschlüssel auf spieler
              betrag      → Ganzzahl, Pflicht, muss größer als 0 sein
              zeitpunkt   → Datum+Uhrzeit, Standardwert CURRENT_TIMESTAMP
            Zusätzlich: Pro Auktion darf derselbe Betrag nur EINMAL geboten werden.
        """,
        "loesung": """CREATE TABLE gebote (
            gebot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            auktion_id INT NOT NULL REFERENCES auktionen(auktion_id) ON DELETE CASCADE,
            spieler_id INT NOT NULL REFERENCES spieler(spieler_id),
            betrag INT NOT NULL CHECK (betrag > 0),
            zeitpunkt DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (auktion_id, betrag));""",
        "tests": ["INSERT INTO gebote (auktion_id, spieler_id, betrag) VALUES (1, 1, 3100)",
                  "INSERT INTO gebote (auktion_id, spieler_id, betrag) VALUES (1, 2, 3200)",
                  "INSERT INTO gebote (auktion_id, spieler_id, betrag) VALUES (2, 3, 25)",
                  "INSERT INTO gebote (auktion_id, spieler_id, betrag) VALUES (2, 4, 3100)",
                  "INSERT INTO gebote (auktion_id, spieler_id, betrag) VALUES (1, 5, 3100)",
                  "INSERT INTO gebote (auktion_id, spieler_id, betrag) VALUES (1, 5, 0)",
                  "INSERT INTO gebote (auktion_id, spieler_id, betrag) VALUES (1, 5, NULL)",
                  "INSERT INTO gebote (auktion_id, spieler_id, betrag) VALUES (7, 5, 50)",
                  "INSERT INTO gebote (auktion_id, spieler_id, betrag) VALUES (1, 77, 50)",
                  "INSERT INTO gebote (auktion_id, spieler_id, betrag) VALUES (NULL, 5, 51)",
                  "INSERT INTO gebote (auktion_id, betrag) VALUES (1, 52)",
                  "DELETE FROM auktionen WHERE auktion_id = 2"],
        "pruefung": ["SELECT gebot_id, auktion_id, spieler_id, betrag FROM gebote ORDER BY gebot_id",
                     "SELECT COUNT(*) AS ohne_zeitpunkt FROM gebote WHERE zeitpunkt IS NULL"],
        "hinweise": ["auktion_id INT NOT NULL REFERENCES auktionen(auktion_id) ON DELETE CASCADE",
                     "zeitpunkt DATETIME DEFAULT CURRENT_TIMESTAMP", "UNIQUE (auktion_id, betrag) am Ende"],
    },
}
