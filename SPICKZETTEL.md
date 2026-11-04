# SQL-Spickzettel (MySQL-Schreibweise)

## Teilsprachen
| | Befehle |
|---|---|
| DDL | CREATE, ALTER, DROP, TRUNCATE, RENAME |
| DML | INSERT, UPDATE, DELETE |
| DQL | SELECT |
| DCL | GRANT, REVOKE |
| TCL | START TRANSACTION, COMMIT, ROLLBACK, SAVEPOINT |

## Tabellen & Constraints
```sql
CREATE DATABASE IF NOT EXISTS rpg_spielwelt DEFAULT CHARACTER SET utf8mb4;
USE rpg_spielwelt;

CREATE TABLE IF NOT EXISTS spieler (
    spieler_id   INT AUTO_INCREMENT PRIMARY KEY,
    spieler_name VARCHAR(50) NOT NULL UNIQUE,
    klasse       ENUM('Krieger','Magier','Schurke','Priester') NOT NULL,
    level        INT NOT NULL DEFAULT 1 CHECK (level BETWEEN 1 AND 100),
    gold         DECIMAL(10,2) DEFAULT 0,
    erstellt_am  DATE,
    gilde_id     INT,
    CONSTRAINT fk_spieler_gilde FOREIGN KEY (gilde_id)
        REFERENCES gilden(gilde_id) ON DELETE SET NULL ON UPDATE CASCADE
);
-- zusammengesetzter Schlüssel:  PRIMARY KEY (spieler_id, quest_id)
-- mehrspaltig eindeutig:        UNIQUE (vorname, nachname)

ALTER TABLE spieler ADD COLUMN xp INT DEFAULT 0;
ALTER TABLE spieler MODIFY COLUMN klasse VARCHAR(30);        -- nur MySQL
ALTER TABLE spieler RENAME COLUMN xp TO erfahrung;
ALTER TABLE spieler DROP COLUMN erfahrung;
ALTER TABLE spieler ADD CONSTRAINT fk_x FOREIGN KEY (gilde_id) REFERENCES gilden(gilde_id);
RENAME TABLE monster TO kreaturen;
DROP TABLE IF EXISTS alt;   TRUNCATE TABLE inventar;
CREATE TABLE kopie AS SELECT * FROM gegenstaende WHERE typ = 'Waffe';
```
ON DELETE: `RESTRICT`/`NO ACTION` (Standard: verbieten) · `CASCADE` (mitlöschen) · `SET NULL`

## CRUD
```sql
INSERT INTO gilden (gildenname, gruendungsjahr) VALUES ('A', 2020), ('B', 2021);
INSERT INTO inventar (spieler_id, gegenstand_id, anzahl) SELECT spieler_id, 1, 1 FROM spieler WHERE ...;
UPDATE spieler SET level = level + 1, gold = 0 WHERE klasse = 'Krieger';
DELETE FROM quests WHERE belohnung_gold < 100;
START TRANSACTION; ... COMMIT;   -- oder ROLLBACK;
INSERT ... ON DUPLICATE KEY UPDATE anzahl = anzahl + 1;   -- Upsert
```

## SELECT – Schreib- vs. Ausführungsreihenfolge
```
SELECT [DISTINCT] spalten, AGG(x) AS alias   5
FROM tabelle t  [JOIN ... ON ...]            1
WHERE zeilenbedingung                        2
GROUP BY spalten                             3
HAVING gruppenbedingung                      4
ORDER BY spalte [ASC|DESC]                   6
LIMIT anzahl OFFSET start;                   7     (MySQL auch: LIMIT start, anzahl)
```

## WHERE
`= <> != < > <= >=` · `AND OR NOT` (AND vor OR → Klammern!) · `BETWEEN a AND b` (inklusiv)
· `IN ('a','b')` · `LIKE 'A%'` (`%` beliebig viele, `_` genau eins) · `IS NULL` / `IS NOT NULL` (nie `= NULL`)

## Funktionen
| Text | Zahl | Datum | NULL / Logik |
|---|---|---|---|
| CONCAT, CONCAT_WS | ROUND(x, 2) | NOW(), CURDATE() | COALESCE(a, b, ...) |
| UPPER, LOWER | CEIL, FLOOR | YEAR, MONTH, DAY | IFNULL(a, b) |
| LENGTH / CHAR_LENGTH | ABS, MOD / % | DATEDIFF(a, b) | NULLIF(a, b) |
| SUBSTRING(s, start, len) | TRUNCATE(x, d) | DATE_FORMAT(d, '%d.%m.%Y') | IF(bed, a, b) |
| LEFT, RIGHT, REPLACE, TRIM | CAST(x AS SIGNED) | DATE_ADD(d, INTERVAL 7 DAY) | CASE WHEN ... THEN ... ELSE ... END |

## Aggregate
`COUNT(*)` alle Zeilen · `COUNT(spalte)` ohne NULL · `COUNT(DISTINCT x)` · `SUM AVG MIN MAX` (ignorieren NULL)
· `GROUP_CONCAT(x ORDER BY x SEPARATOR ', ')`
· Regel: Jede SELECT-Spalte steht im GROUP BY **oder** in einer Aggregatfunktion.
· WHERE filtert Zeilen **vor** dem Gruppieren, HAVING filtert Gruppen **danach**.
· Fenster: `RANK() OVER (PARTITION BY klasse ORDER BY level DESC)`, `SUM(x) OVER (ORDER BY datum)`

## Unterabfragen
```sql
WHERE level > (SELECT AVG(level) FROM spieler)                    -- skalar
WHERE id IN (SELECT ...)      WHERE id NOT IN (SELECT ... WHERE x IS NOT NULL)  -- NULL-Falle!
WHERE EXISTS (SELECT 1 FROM spieler s WHERE s.gilde_id = g.gilde_id)  -- korreliert
FROM (SELECT ...) AS t                                            -- Alias Pflicht
WITH t AS (SELECT ...) SELECT ... FROM t;                         -- CTE
```

## Joins
| Join | Ergebnis |
|---|---|
| `INNER JOIN` | nur Zeilen mit Partner auf beiden Seiten |
| `LEFT JOIN` | alle links + Partner (sonst NULL) |
| `RIGHT JOIN` | alle rechts + Partner |
| `FULL OUTER` | MySQL: `LEFT JOIN ... UNION ... RIGHT JOIN` |
| `CROSS JOIN` | jede mit jeder (n × m) |
| Self Join | `FROM spieler a JOIN spieler b ON ...` |
| Anti-Join | `LEFT JOIN b ON ... WHERE b.id IS NULL` |

Bedingung für die rechte Tabelle beim LEFT JOIN → ins `ON`, nicht ins `WHERE`.
Nach LEFT JOIN: `COUNT(b.id)` statt `COUNT(*)`. Bei Vervielfachung: `COUNT(DISTINCT ...)`.

## Normalisierung
- **Anomalien:** Einfüge-, Änderungs-, Löschanomalie
- **1NF:** atomare Werte, keine Wiederholungsgruppen
- **2NF:** 1NF + keine partielle Abhängigkeit (Teil eines zusammengesetzten Schlüssels)
- **3NF:** 2NF + keine transitive Abhängigkeit (Nicht-Schlüssel → Nicht-Schlüssel)
- **Beziehungen:** 1:n → FK auf n-Seite · n:m → Zwischentabelle · 1:1 → FK + UNIQUE

## Performance & Sicherheit
```sql
CREATE INDEX idx_monster_gebiet_stufe ON monster (gebiet, stufe);   -- Linkspräfix-Regel!
CREATE UNIQUE INDEX idx_name ON gegenstaende (name);
DROP INDEX idx_name ON gegenstaende;
EXPLAIN SELECT ...;           -- type ALL = Full Scan, ref/range = Index
```
Index wird **nicht** genutzt bei: Funktion/Rechnung auf der Spalte, `LIKE '%x'`, fehlender erster Index-Spalte.
ACID = Atomicity, Consistency, Isolation, Durability.
`GRANT SELECT ON db.* TO 'user'@'host';` · `REVOKE ...` · gegen SQL-Injection: Prepared Statements.
