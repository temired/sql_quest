-- =====================================================================
-- RPG-Spielwelt (Daten aus dem Unterricht + ein paar Extras für NULL-Fälle)
-- Extras: 3 Spieler ohne Gilde (16-18), 1 Gegenstand ohne Wert/Beschreibung (16),
--         1 Quest ohne Zielmonster (16), ein paar zusätzliche Inventar-Einträge.
-- =====================================================================

CREATE TABLE gilden (
    gilde_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    gildenname      VARCHAR(50) NOT NULL UNIQUE,
    gruendungsjahr  INT
);

CREATE TABLE spieler (
    spieler_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    spieler_name  VARCHAR(50) NOT NULL UNIQUE,
    klasse        VARCHAR(20) NOT NULL,
    level         INT NOT NULL DEFAULT 1 CHECK (level BETWEEN 1 AND 100),
    erstellt_am   DATE,
    gilde_id      INT REFERENCES gilden(gilde_id) ON DELETE SET NULL
);

CREATE TABLE gegenstaende (
    gegenstand_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name           VARCHAR(50) NOT NULL,
    typ            VARCHAR(20),
    seltenheit     VARCHAR(20),
    wert           INT,
    beschreibung   TEXT
);

CREATE TABLE inventar (
    inventar_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    spieler_id     INT NOT NULL REFERENCES spieler(spieler_id) ON DELETE CASCADE,
    gegenstand_id  INT NOT NULL REFERENCES gegenstaende(gegenstand_id),
    anzahl         INT NOT NULL DEFAULT 1 CHECK (anzahl > 0)
);

CREATE TABLE monster (
    monster_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(50) NOT NULL,
    gebiet      VARCHAR(50),
    stufe       INT,
    ist_boss    BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE quests (
    quest_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    titel            VARCHAR(100) NOT NULL,
    belohnung_gold   INT,
    ziel_monster_id  INT REFERENCES monster(monster_id)
);

INSERT INTO gilden (gildenname, gruendungsjahr) VALUES
('DragonSlayers', 2022), ('ShadowMages', 2024), ('IronForge', 2020), ('NightWatch', 2021),
('MysticBrothers', 2019), ('StormBringers', 2023), ('StarGazers', 2025), ('BloodHounds', 2018),
('SilverShields', 2022), ('VoidWalkers', 2024), ('PhoenixLegion', 2020), ('WildCards', 2025),
('SunCrest', 2021), ('DoomSlayers', 2017), ('CrystalGuards', 2023);

INSERT INTO spieler (spieler_name, klasse, level, erstellt_am, gilde_id) VALUES
('ShadowKnight', 'Krieger', 12, '2023-01-15', 1),
('PixelElf', 'Magier', 10, '2023-03-22', 2),
('NoobSlayer', 'Schurke', 5, '2023-05-10', 1),
('HealBot', 'Priester', 11, '2023-06-01', 2),
('TankMaster', 'Krieger', 18, '2022-11-05', 3),
('FireMage', 'Magier', 15, '2022-12-19', 3),
('RogueOne', 'Schurke', 7, '2024-01-08', 4),
('HolyShield', 'Priester', 9, '2024-02-14', 4),
('BerserkerBob', 'Krieger', 20, '2021-08-30', 5),
('ManaAddict', 'Magier', 14, '2022-04-11', 5),
('StealthySue', 'Schurke', 12, '2023-09-17', 6),
('DivineGrace', 'Priester', 8, '2023-10-05', 6),
('IronWall', 'Krieger', 16, '2022-07-20', 7),
('FrostWitch', 'Magier', 13, '2023-08-12', 7),
('ShadowStalker', 'Schurke', 11, '2024-01-02', 8),
('LoneWolf', 'Schurke', 6, '2024-03-01', NULL),
('Newbie99', 'Magier', 1, '2024-05-20', NULL),
('GhostRider', 'Krieger', 3, '2024-04-11', NULL);

INSERT INTO gegenstaende (name, typ, seltenheit, wert, beschreibung) VALUES
('Heiltrank', 'Trank', 'Gewöhnlich', 50, 'Stellt sofort einen Teil der Lebenspunkte wieder her.'),
('Manatrank', 'Trank', 'Gewöhnlich', 40, 'Regeneriert magische Energie im Eiltempo.'),
('Flammenschwert', 'Waffe', 'Episch', 1200, 'Eine Klinge, die permanent in magischen Flammen gehüllt ist.'),
('Eisenhelm', 'Rüstung', 'Gewöhnlich', 150, 'Schützt den Kopf vor leichten Hieben.'),
('Drachenbogen', 'Waffe', 'Legendär', 3500, 'Gefertigt aus den Sehnen eines antiken Ur-Drachens.'),
('Lederrüstung', 'Rüstung', 'Gewöhnlich', 80, 'Bietet gute Beweglichkeit bei mittlerem Schutz.'),
('Schattenumhang', 'Rüstung', 'Selten', 450, 'Lässt den Träger im Halbdunkel verschwinden.'),
('Kristallstab', 'Waffe', 'Selten', 600, 'Fokussiert arkane Energien mit extremer Präzision.'),
('Lebenselixier', 'Trank', 'Selten', 200, 'Ein Gebräu von Alchemisten, das lebensrettend sein kann.'),
('Titanschild', 'Rüstung', 'Episch', 1500, 'Fast unzerstörbar, selbst von Riesenhand geschlagen.'),
('Giftklinge', 'Waffe', 'Selten', 700, 'Klinge ist mit tödlichem Säuregift benetzt.'),
('Elfenstiefel', 'Rüstung', 'Selten', 300, 'Ermöglichen lautloses Gehen auf jedem Untergrund.'),
('Feuermantel', 'Rüstung', 'Episch', 1100, 'Wehrt Angreifer durch heiße Hitzewellen ab.'),
('Ausdauerbrot', 'Nahrung', 'Gewöhnlich', 10, 'Hält Abenteurer tagelang satt.'),
('Seelenklinge', 'Waffe', 'Legendär', 5000, 'Raubt gefallenen Gegnern die Lebenskraft.'),
('Mysteriöses Amulett', 'Schmuck', 'Legendär', NULL, NULL);

INSERT INTO inventar (spieler_id, gegenstand_id, anzahl) VALUES
(1, 1, 5), (1, 3, 1), (2, 2, 3), (2, 5, 1), (3, 1, 1), (3, 4, 1), (4, 2, 4), (4, 9, 2),
(5, 10, 1), (6, 8, 1), (7, 11, 1), (8, 12, 1), (9, 15, 1), (10, 13, 1), (11, 7, 2),
(12, 1, 2), (13, 10, 1), (14, 8, 1), (15, 11, 1), (9, 1, 10), (16, 16, 1);

INSERT INTO monster (name, gebiet, stufe, ist_boss) VALUES
('Goblin', 'Elchwald', 2, 0), ('Ork-Krieger', 'Dunkeleisenberge', 6, 0), ('Eisdrache', 'Frostgipfel', 15, 1),
('Schleim', 'Sumpf von Sorrow', 1, 0), ('Waldspinne', 'Elchwald', 3, 0), ('Skelett-Krieger', 'Verlassene Gruft', 5, 0),
('Dunkelelf-Assassine', 'Schattenwald', 8, 0), ('Höhlentroll', 'Dunkeleisenberge', 10, 0), ('Feuerelementar', 'Vulkanherz', 12, 0),
('Harpyie', 'Sturmklippen', 7, 0), ('Zombie', 'Verlassene Gruft', 4, 0), ('Werwolf', 'Nebelwald', 9, 0),
('Wassermonster', 'Blauer See', 6, 0), ('Riesenspinne', 'Sumpf von Sorrow', 5, 0), ('Endboss Malakor', 'Turm der Verdammnis', 20, 1);

INSERT INTO quests (titel, belohnung_gold, ziel_monster_id) VALUES
('Goblins im Wald', 100, 1), ('Die Festung der Orks', 500, 2), ('Jagd auf den Frostgipfel', 2000, 3),
('Schleim-Plage im Sumpf', 80, 4), ('Spinnenjagd im Unterholz', 150, 5), ('Säuberung der Gruft', 300, 6),
('Schatten im Schattenwald', 600, 7), ('Der Troll in der Höhle', 750, 8), ('Hitze im Vulkan', 1200, 9),
('Harpyien über den Wolken', 450, 10), ('Untote Rache', 350, 11), ('Der Wolfspfad', 550, 12),
('Geheimnisse des Sees', 400, 13), ('Netze des Schreckens', 320, 14), ('Der Sturm auf Malakors Turm', 5000, 15),
('Kräuter sammeln', 30, NULL);
