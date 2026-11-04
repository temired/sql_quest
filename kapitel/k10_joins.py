KAPITEL = {
    "nr": 10,
    "titel": "Joins",
    "lektionen": [
        {
            "titel": "INNER JOIN",
            "theorie": """
                # Daten aus mehreren Tabellen zusammenführen
                Spieler stehen in `spieler`, Gildennamen in `gilden`. Verbunden über gilde_id.

                    SELECT spieler.spieler_name, gilden.gildenname
                    FROM spieler
                    INNER JOIN gilden ON spieler.gilde_id = gilden.gilde_id;

                * `ON` gibt die Verbindungsbedingung an (meist: Fremdschlüssel = Primärschlüssel).
                * INNER JOIN liefert nur Zeilen, die auf BEIDEN Seiten einen Partner haben.
                  → Spieler ohne Gilde und Gilden ohne Spieler fallen weg!
                * `JOIN` allein bedeutet `INNER JOIN`.
                ---
                # Tabellen-Aliase – kürzer und Pflicht bei Mehrdeutigkeit
                    SELECT s.spieler_name, s.level, g.gildenname
                    FROM spieler s
                    JOIN gilden g ON s.gilde_id = g.gilde_id
                    WHERE g.gildenname = 'DragonSlayers';

                Gibt es eine Spalte in beiden Tabellen (gilde_id), MUSS man sagen, welche gemeint ist:
                `s.gilde_id` – sonst Fehler "ambiguous column name".
                ---
                # Was passiert intern? Das kartesische Produkt
                Ohne ON kombiniert die DB JEDE Zeile links mit JEDER Zeile rechts:
                18 Spieler × 15 Gilden = 270 Zeilen (CROSS JOIN). Das ON filtert dann die passenden heraus.

                    -- alte Schreibweise (funktioniert, aber vermeiden):
                    SELECT s.spieler_name, g.gildenname FROM spieler s, gilden g WHERE s.gilde_id = g.gilde_id;
                ! `JOIN ... USING (gilde_id)` geht, wenn die Spalte in beiden Tabellen gleich heißt.
                ! `NATURAL JOIN` verbindet automatisch über ALLE gleichnamigen Spalten – gefährlich, nicht benutzen.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige spieler_name, klasse und gildenname aller Spieler, die in einer Gilde sind.",
                    "loesung": "SELECT s.spieler_name, s.klasse, g.gildenname FROM spieler s INNER JOIN gilden g ON s.gilde_id = g.gilde_id;",
                    "hinweise": ["FROM spieler s JOIN gilden g ON s.gilde_id = g.gilde_id"],
                },
                {
                    "aufgabe": "Zeige spieler_name und level aller Mitglieder der Gilde 'IronForge'.",
                    "loesung": "SELECT s.spieler_name, s.level FROM spieler s JOIN gilden g ON s.gilde_id = g.gilde_id WHERE g.gildenname = 'IronForge';",
                },
                {
                    "aufgabe": "Zeige für jede Quest: titel AS `quest`, belohnung_gold, den Monsternamen AS `ziel` und die stufe des Monsters.",
                    "loesung": "SELECT q.titel AS quest, q.belohnung_gold, m.name AS ziel, m.stufe FROM quests q JOIN monster m ON q.ziel_monster_id = m.monster_id;",
                    "spalten": True,
                },
                {
                    "aufgabe": "Zeige titel und belohnung_gold aller Quests, deren Zielmonster ein Boss ist.",
                    "loesung": "SELECT q.titel, q.belohnung_gold FROM quests q JOIN monster m ON q.ziel_monster_id = m.monster_id WHERE m.ist_boss = 1;",
                },
                {
                    "typ": "quiz",
                    "aufgabe": "Wie viele Zeilen liefert `SELECT * FROM spieler, gilden;` (18 Spieler, 15 Gilden)?",
                    "optionen": ["15", "18", "33", "270"],
                    "richtig": 4,
                    "erklaerung": "Ohne Bedingung: kartesisches Produkt = 18 × 15 = 270.",
                },
            ],
        },
        {
            "titel": "Mehrere Joins (n:m)",
            "theorie": """
                # Drei Tabellen: Spieler – Inventar – Gegenstände
                `inventar` ist die Zwischentabelle der n:m-Beziehung. Um Spielernamen UND Gegenstandsnamen
                zu sehen, braucht man zwei Joins:

                    SELECT s.spieler_name, g.name AS gegenstand, i.anzahl
                    FROM spieler s
                    JOIN inventar i      ON s.spieler_id = i.spieler_id
                    JOIN gegenstaende g  ON i.gegenstand_id = g.gegenstand_id;

                * Jeder weitere JOIN hängt sich an das bisherige Zwischenergebnis.
                * Auf alle Tabellen kann man danach in SELECT, WHERE, ORDER BY zugreifen.
                * Faustregel: n Tabellen brauchen n-1 Join-Bedingungen.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige spieler_name, den Gegenstandsnamen (`gegenstand`) und die anzahl für alle Inventar-Einträge.",
                    "loesung": """SELECT s.spieler_name, g.name AS gegenstand, i.anzahl FROM spieler s
                        JOIN inventar i ON s.spieler_id = i.spieler_id JOIN gegenstaende g ON i.gegenstand_id = g.gegenstand_id;""",
                    "spalten": True,
                },
                {
                    "aufgabe": """
                        Zeige spieler_name, Gegenstandsname (`item`), anzahl, wert (`einzelwert`) und anzahl * wert (`gesamtwert`).
                        Sortiert nach spieler_name, dann gesamtwert absteigend.
                    """,
                    "loesung": """SELECT s.spieler_name, g.name AS item, i.anzahl, g.wert AS einzelwert, i.anzahl * g.wert AS gesamtwert
                        FROM spieler s JOIN inventar i ON s.spieler_id = i.spieler_id JOIN gegenstaende g ON i.gegenstand_id = g.gegenstand_id
                        ORDER BY s.spieler_name, gesamtwert DESC;""",
                    "spalten": True,
                },
                {
                    "aufgabe": "Zeige spieler_name, klasse und Gegenstandsname (`item`) aller Spieler, die einen Gegenstand mit Seltenheit 'Legendär' besitzen.",
                    "loesung": """SELECT s.spieler_name, s.klasse, g.name AS item FROM spieler s
                        JOIN inventar i ON s.spieler_id = i.spieler_id JOIN gegenstaende g ON i.gegenstand_id = g.gegenstand_id
                        WHERE g.seltenheit = 'Legendär';""",
                    "spalten": True,
                },
                {
                    "aufgabe": "Zeige spieler_name, gildenname und Gegenstandsname (`item`) aller WAFFEN, die Gildenmitglieder besitzen (4 Tabellen!).",
                    "loesung": """SELECT s.spieler_name, gi.gildenname, g.name AS item FROM spieler s
                        JOIN gilden gi ON s.gilde_id = gi.gilde_id
                        JOIN inventar i ON s.spieler_id = i.spieler_id
                        JOIN gegenstaende g ON i.gegenstand_id = g.gegenstand_id
                        WHERE g.typ = 'Waffe';""",
                    "spalten": True,
                    "hinweise": ["Zwei Tabellen beginnen mit g – nimm z.B. gi für gilden und g für gegenstaende."],
                },
            ],
        },
        {
            "titel": "LEFT & RIGHT JOIN",
            "theorie": """
                # LEFT JOIN – alle Zeilen der LINKEN Tabelle behalten
                    SELECT g.gildenname, s.spieler_name
                    FROM gilden g
                    LEFT JOIN spieler s ON g.gilde_id = s.gilde_id;

                * Jede Gilde erscheint – auch ohne Mitglieder. Dann steht bei spieler_name NULL.
                * "Links" = die Tabelle im FROM (vor dem JOIN).
                * RIGHT JOIN = dasselbe andersherum (alle Zeilen der rechten Tabelle).
                  `A RIGHT JOIN B` = `B LEFT JOIN A`. In der Praxis schreibt man fast immer LEFT JOIN.

                    INNER:  A ∩ B             LEFT: ganz A + passendes B          RIGHT: ganz B + passendes A
                ---
                # Anti-Join: "Was hat KEINEN Partner?"
                    SELECT g.gildenname
                    FROM gilden g
                    LEFT JOIN spieler s ON g.gilde_id = s.gilde_id
                    WHERE s.spieler_id IS NULL;
                → Gilden ohne Mitglieder. (Gleiches Ergebnis wie NOT EXISTS aus Kapitel 8.)
                ---
                # ⚠ ON oder WHERE? Die LEFT-JOIN-Falle
                "Alle Monster, und – falls vorhanden – ihre Quests mit über 500 Gold":
                    -- FALSCH: WHERE wirft die Monster ohne passende Quest wieder raus (wird zum INNER JOIN)
                    SELECT m.name, q.titel FROM monster m LEFT JOIN quests q ON q.ziel_monster_id = m.monster_id
                    WHERE q.belohnung_gold > 500;
                    -- RICHTIG: Bedingung für die rechte Tabelle gehört ins ON
                    SELECT m.name, q.titel FROM monster m LEFT JOIN quests q
                        ON q.ziel_monster_id = m.monster_id AND q.belohnung_gold > 500;
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige ALLE Gilden mit ihren Mitgliedern: gildenname, spieler_name. Gilden ohne Mitglieder sollen auch erscheinen.",
                    "loesung": "SELECT g.gildenname, s.spieler_name FROM gilden g LEFT JOIN spieler s ON g.gilde_id = s.gilde_id;",
                    "falsch": ["SELECT g.gildenname, s.spieler_name FROM gilden g JOIN spieler s ON g.gilde_id = s.gilde_id;"],
                },
                {
                    "aufgabe": "Zeige gildenname und gruendungsjahr aller Gilden OHNE Mitglieder (LEFT JOIN + IS NULL).",
                    "loesung": "SELECT g.gildenname, g.gruendungsjahr FROM gilden g LEFT JOIN spieler s ON g.gilde_id = s.gilde_id WHERE s.spieler_id IS NULL;",
                    "muss_enthalten": ["LEFT JOIN"],
                },
                {
                    "aufgabe": "Zeige name, typ und wert aller Gegenstände, die in KEINEM Inventar liegen (Anti-Join).",
                    "loesung": "SELECT g.name, g.typ, g.wert FROM gegenstaende g LEFT JOIN inventar i ON g.gegenstand_id = i.gegenstand_id WHERE i.inventar_id IS NULL;",
                    "muss_enthalten": ["JOIN"],
                },
                {
                    "aufgabe": "Zeige mit einem RIGHT JOIN (inventar links, gegenstaende rechts) alle Gegenstände (name) und die anzahl aus dem Inventar – auch Gegenstände ohne Inventar-Eintrag.",
                    "loesung": "SELECT g.name, i.anzahl FROM inventar i RIGHT JOIN gegenstaende g ON i.gegenstand_id = g.gegenstand_id;",
                    "muss_enthalten": ["RIGHT JOIN"],
                },
                {
                    "aufgabe": "Zeige ALLE Monster (name) und – falls vorhanden – den titel ihrer Quest, aber nur Quests mit MEHR als 500 Gold. Monster ohne solche Quest bekommen NULL.",
                    "loesung": "SELECT m.name, q.titel FROM monster m LEFT JOIN quests q ON q.ziel_monster_id = m.monster_id AND q.belohnung_gold > 500;",
                    "falsch": ["SELECT m.name, q.titel FROM monster m LEFT JOIN quests q ON q.ziel_monster_id = m.monster_id WHERE q.belohnung_gold > 500;"],
                    "hinweise": ["Die Gold-Bedingung gehört ins ON, nicht ins WHERE."],
                },
            ],
        },
        {
            "titel": "FULL OUTER, CROSS & SELF JOIN",
            "theorie": """
                # FULL OUTER JOIN – alles von beiden Seiten
                    SELECT s.spieler_name, g.gildenname
                    FROM spieler s
                    FULL OUTER JOIN gilden g ON s.gilde_id = g.gilde_id;
                → Spieler ohne Gilde UND Gilden ohne Spieler, jeweils mit NULL auf der anderen Seite.

                ! MySQL kennt KEIN FULL OUTER JOIN! Man baut ihn mit UNION nach:
                    SELECT s.spieler_name, g.gildenname FROM spieler s LEFT JOIN gilden g ON s.gilde_id = g.gilde_id
                    UNION
                    SELECT s.spieler_name, g.gildenname FROM spieler s RIGHT JOIN gilden g ON s.gilde_id = g.gilde_id;
                ---
                # CROSS JOIN – jede mit jeder Kombination
                    SELECT s.spieler_name, m.name FROM spieler s CROSS JOIN monster m;
                Sinnvoll für: alle Größen × alle Farben, Kalender × Mitarbeiter, Turnier-Paarungen ...
                ---
                # SELF JOIN – eine Tabelle mit sich selbst
                "Welche Spieler sind in derselben Gilde?"
                    SELECT a.spieler_name, b.spieler_name AS partner
                    FROM spieler a
                    JOIN spieler b ON a.gilde_id = b.gilde_id AND a.spieler_id < b.spieler_id;

                * Zwei verschiedene Aliase (a, b) für dieselbe Tabelle – Pflicht!
                * `a.spieler_id < b.spieler_id` verhindert Paare mit sich selbst und doppelte Paare (A-B und B-A).
                * Klassiker: mitarbeiter(id, name, chef_id) → `JOIN mitarbeiter chef ON m.chef_id = chef.id`
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige spieler_name und gildenname so, dass sowohl Spieler ohne Gilde als auch Gilden ohne Spieler vorkommen (FULL OUTER JOIN oder die MySQL-UNION-Variante).",
                    "loesung": "SELECT s.spieler_name, g.gildenname FROM spieler s FULL OUTER JOIN gilden g ON s.gilde_id = g.gilde_id;",
                    "auch_richtig": ["""SELECT s.spieler_name, g.gildenname FROM spieler s LEFT JOIN gilden g ON s.gilde_id = g.gilde_id
                        UNION SELECT s.spieler_name, g.gildenname FROM spieler s RIGHT JOIN gilden g ON s.gilde_id = g.gilde_id;"""],
                },
                {
                    "aufgabe": "Kampfplan: Jeder Krieger soll gegen jeden Boss antreten. Zeige spieler_name und den Monsternamen als `gegner` (CROSS JOIN).",
                    "loesung": "SELECT s.spieler_name, m.name AS gegner FROM spieler s CROSS JOIN monster m WHERE s.klasse = 'Krieger' AND m.ist_boss = 1;",
                    "spalten": True,
                },
                {
                    "aufgabe": "Zeige alle Paare von Spielern in derselben Gilde: `spieler1`, `spieler2` (jedes Paar nur einmal, niemand mit sich selbst).",
                    "loesung": "SELECT a.spieler_name AS spieler1, b.spieler_name AS spieler2 FROM spieler a JOIN spieler b ON a.gilde_id = b.gilde_id AND a.spieler_id < b.spieler_id;",
                    "spalten": True,
                    "hinweise": ["FROM spieler a JOIN spieler b ON a.gilde_id = b.gilde_id AND a.spieler_id < b.spieler_id"],
                },
                {
                    "aufgabe": "Self Join: Zeige Paare von Monstern im selben Gebiet, bei denen das erste eine HÖHERE Stufe hat: `staerker`, `schwaecher`, gebiet.",
                    "loesung": "SELECT a.name AS staerker, b.name AS schwaecher, a.gebiet FROM monster a JOIN monster b ON a.gebiet = b.gebiet AND a.stufe > b.stufe;",
                    "spalten": True,
                },
                {
                    "aufgabe": """
                        Die Tabelle `mitarbeiter` (Setup) hat die Spalten id, name, chef_id. Zeige für jeden Mitarbeiter name und
                        den Namen seines Chefs als `chef` – auch für die Chefin ganz oben (die hat keinen Chef → NULL).
                    """,
                    "setup": """CREATE TABLE mitarbeiter (id INT PRIMARY KEY, name VARCHAR(30), chef_id INT REFERENCES mitarbeiter(id));
                        INSERT INTO mitarbeiter VALUES (1, 'Königin Ada', NULL), (2, 'Hauptmann Bo', 1), (3, 'Schmied Cid', 1),
                        (4, 'Wache Dina', 2), (5, 'Wache Emil', 2), (6, 'Lehrling Fio', 3);""",
                    "loesung": "SELECT m.name, c.name AS chef FROM mitarbeiter m LEFT JOIN mitarbeiter c ON m.chef_id = c.id;",
                    "spalten": True,
                    "hinweise": ["FROM mitarbeiter m LEFT JOIN mitarbeiter c ON m.chef_id = c.id"],
                },
            ],
        },
        {
            "titel": "JOIN + GROUP BY",
            "theorie": """
                # Erst verbinden, dann gruppieren
                    SELECT g.gildenname, COUNT(s.spieler_id) AS mitglieder
                    FROM gilden g
                    LEFT JOIN spieler s ON g.gilde_id = s.gilde_id
                    GROUP BY g.gilde_id, g.gildenname;

                # ⚠ COUNT(*) vs. COUNT(spalte) beim LEFT JOIN
                Eine Gilde ohne Mitglieder ergibt beim LEFT JOIN EINE Zeile mit NULLs.
                * `COUNT(*)` zählt diese Zeile → 1 Mitglied (falsch!)
                * `COUNT(s.spieler_id)` ignoriert NULL → 0 Mitglieder (richtig)
                ---
                # ⚠ Die Vervielfachungs-Falle (Fan-out)
                Joint man spieler mit inventar, erscheint ein Spieler mit 3 Gegenständen 3-mal.
                Zählt man danach Spieler pro Gilde mit COUNT(s.spieler_id), wird er 3-mal gezählt!
                → `COUNT(DISTINCT s.spieler_id)` benutzen.
            """,
            "aufgaben": [
                {
                    "aufgabe": "Zeige für ALLE Gilden gildenname und Anzahl der Mitglieder (`mitglieder`) – Gilden ohne Mitglieder mit 0. Sortiert nach mitglieder absteigend, dann gildenname.",
                    "loesung": """SELECT g.gildenname, COUNT(s.spieler_id) AS mitglieder FROM gilden g LEFT JOIN spieler s ON g.gilde_id = s.gilde_id
                        GROUP BY g.gilde_id, g.gildenname ORDER BY mitglieder DESC, g.gildenname;""",
                    "falsch": ["""SELECT g.gildenname, COUNT(*) AS mitglieder FROM gilden g LEFT JOIN spieler s ON g.gilde_id = s.gilde_id
                        GROUP BY g.gilde_id, g.gildenname ORDER BY mitglieder DESC, g.gildenname;"""],
                    "spalten": True,
                },
                {
                    "aufgabe": "Zeige gildenname und Durchschnittslevel der Mitglieder (`schnitt`, 1 Nachkommastelle) für Gilden mit Mitgliedern – bester Schnitt zuerst, dann gildenname.",
                    "loesung": """SELECT g.gildenname, ROUND(AVG(s.level), 1) AS schnitt FROM gilden g JOIN spieler s ON g.gilde_id = s.gilde_id
                        GROUP BY g.gilde_id, g.gildenname ORDER BY schnitt DESC, g.gildenname;""",
                    "spalten": True,
                },
                {
                    "aufgabe": "Die 5 reichsten Spieler: spieler_name und Summe aus anzahl * wert ihres Inventars (`vermoegen`), absteigend (bei Gleichstand nach spieler_name).",
                    "loesung": """SELECT s.spieler_name, SUM(i.anzahl * g.wert) AS vermoegen FROM spieler s
                        JOIN inventar i ON s.spieler_id = i.spieler_id JOIN gegenstaende g ON i.gegenstand_id = g.gegenstand_id
                        GROUP BY s.spieler_id, s.spieler_name ORDER BY vermoegen DESC, s.spieler_name LIMIT 5;""",
                    "spalten": True,
                },
                {
                    "aufgabe": "Zeige pro klasse die Anzahl verschiedener Gegenstände (`verschiedene_items`), die Spieler dieser Klasse besitzen. Sortiert nach klasse.",
                    "loesung": """SELECT s.klasse, COUNT(DISTINCT i.gegenstand_id) AS verschiedene_items FROM spieler s
                        JOIN inventar i ON s.spieler_id = i.spieler_id GROUP BY s.klasse ORDER BY s.klasse;""",
                    "spalten": True,
                },
                {
                    "aufgabe": "Zeige pro Gebiet (gebiet) die Summe aller Quest-Belohnungen für Monster dieses Gebiets (`gold`), nur Gebiete mit mehr als 500 Gold. Sortiert nach gold absteigend.",
                    "loesung": """SELECT m.gebiet, SUM(q.belohnung_gold) AS gold FROM monster m JOIN quests q ON q.ziel_monster_id = m.monster_id
                        GROUP BY m.gebiet HAVING SUM(q.belohnung_gold) > 500 ORDER BY gold DESC;""",
                    "spalten": True,
                },
            ],
        },
    ],
    "boss": {
        "titel": "Die Gildenrangliste",
        "story": """
            # Der Rat der Gilden will eine offizielle Rangliste.
            Alles, was du gelernt hast, kommt hier zusammen. Vorsicht vor NULL und vor doppelt gezählten Zeilen!
        """,
        "aufgabe": """
            Zeige für JEDE Gilde (auch ohne Mitglieder):
              gildenname,
              `mitglieder`       → Anzahl Mitglieder (0, wenn keine)
              `bester_spieler`   → das höchste Level in der Gilde (NULL, wenn keine Mitglieder)
              `inventarwert`     → Summe anzahl * wert aller Gegenstände ihrer Mitglieder (0, wenn nichts)
            Sortiert nach inventarwert absteigend, dann gildenname.
        """,
        "loesung": """SELECT gi.gildenname,
                COUNT(DISTINCT s.spieler_id) AS mitglieder,
                MAX(s.level) AS bester_spieler,
                COALESCE(SUM(i.anzahl * g.wert), 0) AS inventarwert
            FROM gilden gi
            LEFT JOIN spieler s ON s.gilde_id = gi.gilde_id
            LEFT JOIN inventar i ON i.spieler_id = s.spieler_id
            LEFT JOIN gegenstaende g ON g.gegenstand_id = i.gegenstand_id
            GROUP BY gi.gilde_id, gi.gildenname
            ORDER BY inventarwert DESC, gi.gildenname;""",
        "falsch": ["""SELECT gi.gildenname, COUNT(s.spieler_id) AS mitglieder, MAX(s.level) AS bester_spieler,
                COALESCE(SUM(i.anzahl * g.wert), 0) AS inventarwert FROM gilden gi
                LEFT JOIN spieler s ON s.gilde_id = gi.gilde_id LEFT JOIN inventar i ON i.spieler_id = s.spieler_id
                LEFT JOIN gegenstaende g ON g.gegenstand_id = i.gegenstand_id
                GROUP BY gi.gilde_id, gi.gildenname ORDER BY inventarwert DESC, gi.gildenname;"""],
        "spalten": True,
        "hinweise": ["Drei LEFT JOINs: gilden → spieler → inventar → gegenstaende",
                     "mitglieder: COUNT(DISTINCT s.spieler_id) – sonst zählst du Spieler mehrfach (einmal pro Gegenstand)!",
                     "inventarwert: COALESCE(SUM(...), 0)"],
    },
}
