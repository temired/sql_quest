from ._hilfe import spaltennamen

KAPITEL = {
    "nr": 9,
    "titel": "Normalization",
    "lektionen": [
        {
            "titel": "Redundanz & Anomalien",
            "theorie": """
                # Warum nicht alles in EINE große Tabelle?
                Stell dir vor, alles steht in einer Tabelle `spieler_alles`:

                    spieler_name | klasse  | gildenname    | gilde_gegruendet
                    -------------+---------+---------------+-----------------
                    ShadowKnight | Krieger | DragonSlayers | 2022
                    NoobSlayer   | Schurke | DragonSlayers | 2022
                    PixelElf     | Magier  | ShadowMages   | 2024

                'DragonSlayers, 2022' steht mehrfach da → REDUNDANZ (doppelte Daten).
                Redundanz führt zu ANOMALIEN:
                ---
                # Die drei Anomalien (Prüfungsklassiker!)
                * Änderungsanomalie (Update): Das Gründungsjahr der DragonSlayers war falsch. Man muss es
                  in VIELEN Zeilen ändern – vergisst man eine, ist die DB widersprüchlich.
                * Einfügeanomalie (Insert): Eine neue Gilde ohne Mitglieder kann man nicht eintragen –
                  es gibt ja keine Zeile ohne Spieler.
                * Löschanomalie (Delete): Verlässt PixelElf das Spiel und wird gelöscht, ist auch
                  die Info über die Gilde ShadowMages weg.

                Normalisierung = Tabellen so zerlegen, dass jede Information genau EINMAL gespeichert wird.
            """,
            "aufgaben": [
                {
                    "typ": "quiz",
                    "aufgabe": "In einer Tabelle steht die Adresse eines Kunden bei jeder seiner 50 Bestellungen. Er zieht um, aber nur 49 Zeilen werden geändert. Welche Anomalie ist das?",
                    "optionen": ["Einfügeanomalie", "Änderungsanomalie", "Löschanomalie", "Keine"],
                    "richtig": 2,
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Ein Kurs kann erst in der DB angelegt werden, wenn sich ein Teilnehmer anmeldet. Welche Anomalie?",
                    "optionen": ["Einfügeanomalie", "Änderungsanomalie", "Löschanomalie", "Redundanzanomalie"],
                    "richtig": 1,
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Der einzige Spieler mit dem Gegenstand 'Seelenklinge' wird gelöscht – und damit auch alle Infos (Wert, Beschreibung) zur Seelenklinge. Welche Anomalie?",
                    "optionen": ["Einfügeanomalie", "Änderungsanomalie", "Löschanomalie", "Keine – das ist gewollt"],
                    "richtig": 3,
                },
            ],
        },
        {
            "titel": "Schlüssel & funktionale Abhängigkeit",
            "theorie": """
                # Schlüsselbegriffe
                * Superschlüssel: jede Spaltenkombination, die eine Zeile eindeutig macht
                  (z.B. spieler_id + spieler_name + level – eindeutig, aber unnötig groß).
                * Schlüsselkandidat: MINIMALER Superschlüssel – man kann keine Spalte weglassen
                  (z.B. spieler_id, aber auch spieler_name, weil UNIQUE).
                * Primärschlüssel: der ausgewählte Schlüsselkandidat (spieler_id).
                * Alternativschlüssel: die übrigen Kandidaten (spieler_name).
                * Fremdschlüssel: verweist auf den PK einer anderen Tabelle.
                * Surrogatschlüssel: künstliche ID ohne fachliche Bedeutung.
                * Zusammengesetzter Schlüssel: besteht aus mehreren Spalten.
                ---
                # Funktionale Abhängigkeit (A → B)
                "B hängt funktional von A ab" = Kenne ich A, kenne ich B eindeutig.
                    spieler_id → spieler_name, klasse, level     (aus der ID folgt alles andere)
                    gilde_id   → gildenname, gruendungsjahr

                * Voll funktional abhängig: B hängt vom GANZEN (zusammengesetzten) Schlüssel ab.
                * Partiell abhängig: B hängt nur von einem TEIL des Schlüssels ab.  → verletzt 2NF
                * Transitiv abhängig: A → B → C, C hängt über ein Nicht-Schlüssel-Attribut ab. → verletzt 3NF
                    spieler_id → gilde_id → gildenname   (gildenname transitiv von spieler_id)
            """,
            "aufgaben": [
                {
                    "typ": "quiz",
                    "aufgabe": "In `spieler` sind sowohl spieler_id als auch spieler_name eindeutig. spieler_id ist der PK. Was ist spieler_name?",
                    "optionen": ["Fremdschlüssel", "Alternativschlüssel (Schlüsselkandidat)", "Superschlüssel, aber kein Kandidat", "Gar kein Schlüssel"],
                    "richtig": 2,
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Tabelle inventar_alt(spieler_id, gegenstand_id, anzahl, gegenstand_name) mit PK (spieler_id, gegenstand_id). Wie hängt gegenstand_name ab?",
                    "optionen": ["voll funktional vom PK", "partiell – nur von gegenstand_id", "transitiv über anzahl", "gar nicht"],
                    "richtig": 2,
                    "erklaerung": "gegenstand_name folgt allein aus gegenstand_id (Teil des Schlüssels) → partielle Abhängigkeit → verletzt 2NF.",
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Tabelle spieler_alt(spieler_id PK, spieler_name, gilde_id, gildenname). Welche Abhängigkeit verletzt hier die 3NF?",
                    "optionen": ["spieler_id → spieler_name", "spieler_id → gilde_id", "gilde_id → gildenname (transitiv)", "Keine"],
                    "richtig": 3,
                },
            ],
        },
        {
            "titel": "1. Normalform",
            "theorie": """
                # 1NF: Alle Werte sind ATOMAR
                * Jede Zelle enthält genau EINEN Wert (keine Listen, keine Aufzählungen).
                * Keine Wiederholungsgruppen (skill1, skill2, skill3 ...).
                * Jede Zeile ist eindeutig (es gibt einen Primärschlüssel).

                NICHT in 1NF:
                    spieler_name | skills
                    -------------+-----------------------------
                    FireMage     | Feuerball, Meteor
                    HealBot      | Heilen

                In 1NF:
                    spieler_name | skill
                    -------------+----------
                    FireMage     | Feuerball
                    FireMage     | Meteor
                    HealBot      | Heilen

                ? Auch "Name: 'Max Mustermann'" ist streng genommen nicht atomar, wenn man nach
                ? Nachnamen suchen/sortieren will → vorname / nachname trennen. Adresse → strasse, plz, ort.
            """,
            "aufgaben": [
                {
                    "typ": "aendern",
                    "setup": """CREATE TABLE skills_alt (spieler_name VARCHAR(50), skills VARCHAR(200));
                        INSERT INTO skills_alt VALUES ('FireMage', 'Feuerball, Meteor'), ('HealBot', 'Heilen'),
                        ('FrostWitch', 'Eislanze, Frostnova, Blizzard');""",
                    "aufgabe": """
                        Die Tabelle `skills_alt` (schau sie dir mit .s skills_alt an) verletzt die 1NF.
                        Lege `spieler_skills` an mit den Spalten spieler_name (Text 50) und skill (Text 50),
                        Primärschlüssel aus BEIDEN Spalten, und trage alle Skills atomar ein (eine Zeile pro Skill).
                    """,
                    "loesung": """CREATE TABLE spieler_skills (spieler_name VARCHAR(50), skill VARCHAR(50), PRIMARY KEY (spieler_name, skill));
                        INSERT INTO spieler_skills VALUES ('FireMage', 'Feuerball'), ('FireMage', 'Meteor'), ('HealBot', 'Heilen'),
                        ('FrostWitch', 'Eislanze'), ('FrostWitch', 'Frostnova'), ('FrostWitch', 'Blizzard');""",
                    "tests": ["INSERT INTO spieler_skills VALUES ('HealBot', 'Heilen')"],
                    "pruefung": ["SELECT spieler_name, skill FROM spieler_skills ORDER BY spieler_name, skill"],
                    "hinweise": ["CREATE TABLE spieler_skills (spieler_name VARCHAR(50), skill VARCHAR(50), PRIMARY KEY (spieler_name, skill));",
                                 "Dann: INSERT INTO spieler_skills VALUES ('FireMage', 'Feuerball'), ('FireMage', 'Meteor'), ..."],
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Eine Tabelle hat die Spalten waffe1, waffe2, waffe3. Was ist das Problem?",
                    "optionen": ["Keins, das ist normalisiert",
                                 "Wiederholungsgruppe – verletzt die 1NF; besser: eigene Tabelle mit einer Zeile pro Waffe",
                                 "Verletzt nur die 3NF",
                                 "Es fehlt ein Index"],
                    "richtig": 2,
                },
            ],
        },
        {
            "titel": "2. und 3. Normalform",
            "theorie": """
                # 2NF: 1NF + keine PARTIELLEN Abhängigkeiten
                Betrifft nur Tabellen mit ZUSAMMENGESETZTEM Primärschlüssel.
                Jedes Nicht-Schlüssel-Attribut muss vom GANZEN Schlüssel abhängen.

                    inventar_alt (spieler_id, gegenstand_id, anzahl, gegenstand_name, gegenstand_wert)
                    PK = (spieler_id, gegenstand_id)
                    anzahl                       → hängt von beiden ab ✔
                    gegenstand_name, _wert       → hängt nur von gegenstand_id ab ✘

                Lösung: auslagern →  gegenstaende(gegenstand_id, name, wert)  +  inventar(spieler_id, gegenstand_id, anzahl)
                ? Hat eine Tabelle einen einspaltigen PK und ist in 1NF, ist sie automatisch in 2NF.
                ---
                # 3NF: 2NF + keine TRANSITIVEN Abhängigkeiten
                Kein Nicht-Schlüssel-Attribut darf von einem anderen Nicht-Schlüssel-Attribut abhängen.

                    spieler_alt (spieler_id, spieler_name, gilde_id, gildenname, gruendungsjahr)
                    spieler_id → gilde_id → gildenname, gruendungsjahr   ✘ transitiv

                Lösung: spieler(spieler_id, spieler_name, gilde_id)  +  gilden(gilde_id, gildenname, gruendungsjahr)

                ? Merksatz (nach Codd): Jedes Attribut hängt ab vom Schlüssel (1NF), vom ganzen Schlüssel (2NF)
                ? und von nichts als dem Schlüssel (3NF) – "so help me Codd".
                ---
                # BCNF und Denormalisierung
                * BCNF (Boyce-Codd): verschärfte 3NF – JEDE Determinante (linke Seite einer Abhängigkeit)
                  muss ein Schlüsselkandidat sein. In der Praxis selten relevant.
                * 4NF/5NF: mehrwertige Abhängigkeiten – sehr selten.
                * Denormalisierung: BEWUSST Redundanz einbauen, um Lesezugriffe zu beschleunigen
                  (z.B. Data Warehouse, Reporting, vorberechnete Summen). Man nimmt die Anomalie-Gefahr in Kauf.
                * In der Praxis: bis zur 3NF normalisieren ist der Standard.
            """,
            "aufgaben": [
                {
                    "typ": "aendern",
                    "setup": """CREATE TABLE spieler_flach (spieler_name VARCHAR(50) PRIMARY KEY, klasse VARCHAR(20),
                        gildenname VARCHAR(50), gilden_gruendung INT);
                        INSERT INTO spieler_flach VALUES
                        ('Aria', 'Magier', 'Sternenwacht', 2019), ('Bran', 'Krieger', 'Sternenwacht', 2019),
                        ('Cora', 'Priester', 'Eisenfaust', 2021), ('Dax', 'Schurke', 'Eisenfaust', 2021),
                        ('Elin', 'Magier', 'Mondschein', 2023), ('Fynn', 'Krieger', NULL, NULL);""",
                    "aufgabe": """
                        `spieler_flach` verletzt die 3NF (gilden_gruendung hängt von gildenname ab, nicht vom Spieler).
                        Lege `gilden_neu` an: gildenname (Text 50, Primärschlüssel), gruendung (Ganzzahl)
                        und befülle sie mit INSERT ... SELECT DISTINCT aus spieler_flach (nur Zeilen mit Gilde).
                    """,
                    "loesung": """CREATE TABLE gilden_neu (gildenname VARCHAR(50) PRIMARY KEY, gruendung INT);
                        INSERT INTO gilden_neu (gildenname, gruendung)
                        SELECT DISTINCT gildenname, gilden_gruendung FROM spieler_flach WHERE gildenname IS NOT NULL;""",
                    "pruefung": [spaltennamen("gilden_neu"), "SELECT gildenname, gruendung FROM gilden_neu ORDER BY gildenname"],
                    "tests": ["INSERT INTO gilden_neu VALUES ('Sternenwacht', 2000)"],
                    "hinweise": ["INSERT INTO gilden_neu (gildenname, gruendung) SELECT DISTINCT ... FROM spieler_flach WHERE gildenname IS NOT NULL;"],
                },
                {
                    "typ": "aendern",
                    "setup": """CREATE TABLE spieler_flach (spieler_name VARCHAR(50) PRIMARY KEY, klasse VARCHAR(20),
                        gildenname VARCHAR(50), gilden_gruendung INT);
                        INSERT INTO spieler_flach VALUES
                        ('Aria', 'Magier', 'Sternenwacht', 2019), ('Bran', 'Krieger', 'Sternenwacht', 2019),
                        ('Cora', 'Priester', 'Eisenfaust', 2021), ('Fynn', 'Krieger', NULL, NULL);
                        CREATE TABLE gilden_neu (gildenname VARCHAR(50) PRIMARY KEY, gruendung INT);
                        INSERT INTO gilden_neu VALUES ('Sternenwacht', 2019), ('Eisenfaust', 2021);""",
                    "aufgabe": """
                        Zweiter Schritt: `gilden_neu` gibt es schon. Entferne nun aus `spieler_flach` die Spalte
                        `gilden_gruendung` (die steht ja jetzt in gilden_neu). Damit ist spieler_flach in 3NF.
                    """,
                    "loesung": "ALTER TABLE spieler_flach DROP COLUMN gilden_gruendung;",
                    "pruefung": [spaltennamen("spieler_flach"), "SELECT * FROM spieler_flach ORDER BY spieler_name"],
                },
                {
                    "typ": "quiz",
                    "aufgabe": "bestellung(bestell_nr, artikel_nr, menge, artikel_preis) mit PK (bestell_nr, artikel_nr). In welcher Normalform ist sie höchstens?",
                    "optionen": ["0NF", "1NF – artikel_preis hängt nur von artikel_nr ab (partiell)", "2NF", "3NF"],
                    "richtig": 2,
                },
                {
                    "typ": "quiz",
                    "aufgabe": "kunde(kunden_nr PK, name, plz, ort). plz → ort. Welche Normalform ist verletzt?",
                    "optionen": ["1NF", "2NF", "3NF (transitive Abhängigkeit kunden_nr → plz → ort)", "Keine"],
                    "richtig": 3,
                    "erklaerung": "Lehrbuch-korrekt wäre eine Tabelle plz_ort. In der Praxis lässt man das oft bewusst so (Denormalisierung).",
                },
            ],
        },
        {
            "titel": "Beziehungen & ER-Modell",
            "theorie": """
                # Kardinalitäten
                    Beziehung | Beispiel                         | Umsetzung
                    ----------+----------------------------------+--------------------------------------
                    1:1       | Spieler – Account-Einstellungen  | FK + UNIQUE in einer der Tabellen
                    1:n       | Gilde – Spieler                  | FK auf der n-Seite (spieler.gilde_id)
                    n:m       | Spieler – Gegenstände            | ZWISCHENTABELLE (inventar) mit zwei FKs

                * Bei 1:n kommt der Fremdschlüssel IMMER auf die "viele"-Seite.
                * n:m geht in relationalen DBs nicht direkt → Zwischentabelle (auch: Verbindungs-,
                  Koppel-, Assoziationstabelle). Sie kann eigene Attribute haben (`anzahl`).
                ---
                # Vom ER-Modell zum Relationenmodell
                * ERM (Entity-Relationship-Modell): Entitäten (Rechtecke), Attribute (Ellipsen),
                  Beziehungen (Rauten) mit Kardinalitäten (1, n, m) – Chen-Notation.
                * Krähenfuß-Notation (Crow's Foot): ─|─ = genau eins, ─<  = viele, ○ = optional.
                * Min-Max-Notation: (0,n), (1,1) ...
                * Relationenmodell (RM / "RDM" bei euch): Tabellen in Textform, PK unterstrichen, FK mit # oder ↑:
                    spieler(spieler_id, spieler_name, klasse, level, erstellt_am, ↑gilde_id)
                    gilden(gilde_id, gildenname, gruendungsjahr)
                    inventar(inventar_id, ↑spieler_id, ↑gegenstand_id, anzahl)
            """,
            "aufgaben": [
                {
                    "typ": "quiz",
                    "aufgabe": "Welche Beziehung besteht zwischen `spieler` und `gegenstaende` (über `inventar`)?",
                    "optionen": ["1:1", "1:n", "n:m", "keine"],
                    "richtig": 3,
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Eine Gilde hat viele Spieler, ein Spieler ist in höchstens einer Gilde. Wohin kommt der Fremdschlüssel?",
                    "optionen": ["gilden.spieler_id", "spieler.gilde_id", "In eine Zwischentabelle", "In beide Tabellen"],
                    "richtig": 2,
                },
                {
                    "typ": "aendern",
                    "aufgabe": """
                        Spieler können viele Quests annehmen, Quests von vielen Spielern angenommen werden (n:m).
                        Lege die Zwischentabelle `spieler_quests` an:
                          spieler_id    → Fremdschlüssel auf spieler
                          quest_id      → Fremdschlüssel auf quests
                          abgeschlossen → BOOLEAN, Standard 0
                        Primärschlüssel: Kombination aus spieler_id und quest_id.
                    """,
                    "loesung": """CREATE TABLE spieler_quests (
                        spieler_id INT REFERENCES spieler(spieler_id),
                        quest_id INT REFERENCES quests(quest_id),
                        abgeschlossen BOOLEAN DEFAULT 0,
                        PRIMARY KEY (spieler_id, quest_id));""",
                    "tests": ["INSERT INTO spieler_quests (spieler_id, quest_id) VALUES (1, 1)",
                              "INSERT INTO spieler_quests (spieler_id, quest_id) VALUES (1, 2)",
                              "INSERT INTO spieler_quests (spieler_id, quest_id, abgeschlossen) VALUES (2, 1, 1)",
                              "INSERT INTO spieler_quests (spieler_id, quest_id) VALUES (1, 1)",
                              "INSERT INTO spieler_quests (spieler_id, quest_id) VALUES (99, 1)",
                              "INSERT INTO spieler_quests (spieler_id, quest_id) VALUES (1, 99)"],
                    "pruefung": "SELECT spieler_id, quest_id, abgeschlossen FROM spieler_quests ORDER BY spieler_id, quest_id",
                },
                {
                    "typ": "aendern",
                    "aufgabe": """
                        1:1-Beziehung: Jeder Spieler hat höchstens EINE Einstellungs-Zeile. Lege `einstellungen` an:
                          einstellung_id → Primärschlüssel (Ganzzahl), spieler_id → Fremdschlüssel auf spieler, darf nur EINMAL vorkommen,
                          sprache → Text (max. 5), Standard 'de'
                    """,
                    "loesung": """CREATE TABLE einstellungen (einstellung_id INT PRIMARY KEY,
                        spieler_id INT UNIQUE REFERENCES spieler(spieler_id), sprache VARCHAR(5) DEFAULT 'de');""",
                    "tests": ["INSERT INTO einstellungen (einstellung_id, spieler_id) VALUES (1, 1)",
                              "INSERT INTO einstellungen (einstellung_id, spieler_id, sprache) VALUES (2, 2, 'en')",
                              "INSERT INTO einstellungen (einstellung_id, spieler_id) VALUES (3, 1)",
                              "INSERT INTO einstellungen (einstellung_id, spieler_id) VALUES (4, 404)"],
                    "pruefung": "SELECT * FROM einstellungen ORDER BY einstellung_id",
                    "hinweise": ["1:1 = Fremdschlüssel + UNIQUE: spieler_id INT UNIQUE REFERENCES spieler(spieler_id)"],
                },
            ],
        },
    ],
    "boss": {
        "titel": "Der chaotische Handelslog",
        "story": """
            # Der Händlergilde ist ihr Handelsbuch über den Kopf gewachsen.
            Alles steht in EINER Tabelle `handel_flach` – voller Redundanz. Schau sie dir mit .s handel_flach an.
            Normalisiere sie! (Tipp: antwort.sql + .d)
        """,
        "setup": """CREATE TABLE handel_flach (handel_id INT PRIMARY KEY, datum DATE, verkaeufer VARCHAR(50),
                kaeufer VARCHAR(50), item_name VARCHAR(50), item_typ VARCHAR(20), item_seltenheit VARCHAR(20), preis INT);
            INSERT INTO handel_flach VALUES
            (1, '2026-10-01', 'FireMage', 'PixelElf', 'Rubinring', 'Schmuck', 'Selten', 300),
            (2, '2026-10-02', 'HealBot', 'TankMaster', 'Zwergenaxt', 'Waffe', 'Episch', 900),
            (3, '2026-10-02', 'FireMage', 'IronWall', 'Rubinring', 'Schmuck', 'Selten', 320),
            (4, '2026-10-05', 'RogueOne', 'HealBot', 'Nebelphiole', 'Trank', 'Gewöhnlich', 25),
            (5, '2026-10-07', 'PixelElf', 'RogueOne', 'Zwergenaxt', 'Waffe', 'Episch', 850),
            (6, '2026-10-09', 'TankMaster', 'FireMage', 'Nebelphiole', 'Trank', 'Gewöhnlich', 30);""",
        "typ": "aendern",
        "aufgabe": """
            item_typ und item_seltenheit hängen nur vom item_name ab (transitiv) → raus damit!
            1. Lege `items` an: item_name (Text 50, Primärschlüssel), item_typ (Text 20), item_seltenheit (Text 20)
               und befülle sie per INSERT ... SELECT DISTINCT aus handel_flach.
            2. Lege `handel` an: handel_id (Primärschlüssel), datum (Datum), verkaeufer (Text 50), kaeufer (Text 50),
               item_name (Text 50, Pflicht, Fremdschlüssel auf items), preis (Ganzzahl)
               und befülle sie per INSERT ... SELECT aus handel_flach.
            3. Lösche `handel_flach`.
        """,
        "loesung": """
            CREATE TABLE items (item_name VARCHAR(50) PRIMARY KEY, item_typ VARCHAR(20), item_seltenheit VARCHAR(20));
            INSERT INTO items SELECT DISTINCT item_name, item_typ, item_seltenheit FROM handel_flach;
            CREATE TABLE handel (handel_id INT PRIMARY KEY, datum DATE, verkaeufer VARCHAR(50), kaeufer VARCHAR(50),
                item_name VARCHAR(50) NOT NULL REFERENCES items(item_name), preis INT);
            INSERT INTO handel SELECT handel_id, datum, verkaeufer, kaeufer, item_name, preis FROM handel_flach;
            DROP TABLE handel_flach;
        """,
        "tests": ["INSERT INTO handel VALUES (7, '2026-10-10', 'A', 'B', 'Gibtsnicht', 10)",
                  "INSERT INTO handel VALUES (8, '2026-10-10', 'A', 'B', NULL, 10)",
                  "INSERT INTO items VALUES ('Rubinring', 'Schmuck', 'Episch')"],
        "pruefung": ["SELECT name FROM sqlite_master WHERE type = 'table' AND name IN ('items', 'handel', 'handel_flach') ORDER BY name",
                     "SELECT * FROM items ORDER BY item_name",
                     "SELECT * FROM handel ORDER BY handel_id",
                     spaltennamen("handel")],
        "hinweise": ["INSERT INTO items SELECT DISTINCT item_name, item_typ, item_seltenheit FROM handel_flach;",
                     "item_name VARCHAR(50) NOT NULL REFERENCES items(item_name)",
                     "Erst items befüllen, DANN handel (wegen Fremdschlüssel)."],
    },
}
