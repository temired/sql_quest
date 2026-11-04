# SQL-Quest – Vollständiger Lehrplan

Ziel: Nach allen 11 Kapiteln kannst du jede typische Prüfungs- und Praxisaufgabe in SQL lösen
(IHK-Abschlussprüfung FIAE, LF05/LF08, Alltag als Entwickler).
Gespielt wird in der bekannten **RPG-Spielwelt** aus dem Unterricht
(gilden, spieler, gegenstaende, inventar, monster, quests).

Jedes Kapitel = Theorie (seitenweise) → Aufgaben pro Lektion → **Bosskampf** (Abschlussaufgabe).
Prüfung der Antworten: Das Spiel führt deine SQL-Abfrage auf einer frischen Datenbank aus und
vergleicht das Ergebnis mit der Musterlösung (nicht den Text!). Jede richtige Lösung zählt.

Legende: ✅ = mit Übungsaufgabe, 📖 = Theorie/Quiz (geht in SQLite nicht praktisch oder ist reines Wissen)

---

## 1. Einführung
| Thema | Inhalt | |
|---|---|---|
| Datenbank, DBMS, RDBMS | Was ist was, Beispiele (MySQL, MariaDB, PostgreSQL, SQLite, Oracle, MS SQL) | 📖 |
| Relationales Modell | Tabelle (Relation), Zeile (Datensatz/Tupel), Spalte (Attribut), Wert, Schlüssel | 📖 |
| SQL-Sprachfamilien | DDL, DML, DQL, DCL, TCL – welche Befehle gehören wohin | 📖 |
| Syntaxregeln | Semikolon, Groß-/Kleinschreibung, Strings `'...'`, Kommentare `--` und `/* */` | ✅ |
| Erste Abfrage | `SELECT * FROM`, `SELECT spalte FROM` | ✅ |
| MySQL vs. SQLite | Was in diesem Spiel anders ist (USE, SHOW TABLES, DESCRIBE) | 📖 |

## 2. Tabellen (DDL)
| Thema | Inhalt | |
|---|---|---|
| CREATE/DROP DATABASE, USE | Theorie (MySQL) | 📖 |
| Datentypen | INT, BIGINT, DECIMAL(p,s), FLOAT, VARCHAR(n), CHAR(n), TEXT, DATE, DATETIME, TIME, BOOLEAN, ENUM | 📖✅ |
| CREATE TABLE | Spalten + Typen, `IF NOT EXISTS` | ✅ |
| ALTER TABLE | ADD COLUMN, RENAME COLUMN, DROP COLUMN, RENAME TO, (MODIFY in MySQL) | ✅ |
| DROP / TRUNCATE | Unterschied DROP, TRUNCATE, DELETE; `IF EXISTS` | ✅📖 |
| CREATE TABLE AS SELECT | Kopie einer Tabelle | ✅ |

## 3. Constraints (Integrität)
| Thema | Inhalt | |
|---|---|---|
| PRIMARY KEY | Eindeutig + NOT NULL, Surrogat- vs. natürlicher Schlüssel | ✅ |
| AUTO_INCREMENT | Automatische IDs | ✅ |
| NOT NULL, DEFAULT | Pflichtfelder, Standardwerte | ✅ |
| UNIQUE | Eindeutige Werte, mehrere UNIQUE pro Tabelle | ✅ |
| CHECK | Wertebereich prüfen | ✅ |
| FOREIGN KEY | Referentielle Integrität, REFERENCES | ✅ |
| ON DELETE / ON UPDATE | CASCADE, SET NULL, RESTRICT / NO ACTION | ✅ |
| Zusammengesetzter Schlüssel | `PRIMARY KEY (a, b)`, benannte Constraints `CONSTRAINT name` | ✅ |

## 4. CRUD
| Thema | Inhalt | |
|---|---|---|
| CREATE = INSERT | Mit/ohne Spaltenliste, mehrere Zeilen, NULL/DEFAULT, `INSERT ... SELECT` | ✅ |
| READ = SELECT | Wiederholung, Überblick | ✅ |
| UPDATE | `SET` mit WHERE, mehrere Spalten, berechnete Werte | ✅ |
| DELETE | Mit WHERE, Gefahr ohne WHERE, FK-Fehler | ✅ |
| Transaktionen (TCL) | BEGIN/START TRANSACTION, COMMIT, ROLLBACK, ACID | ✅📖 |
| UPSERT | MySQL `ON DUPLICATE KEY UPDATE`, SQLite `ON CONFLICT`, `REPLACE` | 📖 |

## 5. Basic Queries (Einfache Abfragen)
| Thema | Inhalt | |
|---|---|---|
| Spaltenauswahl | `*` vs. Spaltenliste, Aliase `AS` | ✅ |
| Berechnete Spalten | `+ - * /`, Ganzzahldivision-Falle | ✅ |
| DISTINCT | Duplikate entfernen (auch über mehrere Spalten) | ✅ |
| WHERE | `= <> != < > <= >=` | ✅ |
| Logik | AND, OR, NOT, Klammern / Vorrang | ✅ |
| BETWEEN, IN, NOT IN | Bereiche und Listen | ✅ |
| LIKE | `%` und `_`, NOT LIKE | ✅ |
| NULL | `IS NULL`, `IS NOT NULL`, warum `= NULL` nie klappt, Dreiwertige Logik | ✅ |

## 6. Structuring (Ergebnisse strukturieren & formen)
| Thema | Inhalt | |
|---|---|---|
| ORDER BY | ASC/DESC, mehrere Spalten, nach Alias, NULL-Sortierung | ✅ |
| LIMIT / OFFSET | Top-N, Paging, MySQL `LIMIT offset, anzahl` | ✅ |
| CASE WHEN | Fallunterscheidungen, Kategorien bilden | ✅ |
| Textfunktionen | UPPER, LOWER, LENGTH, SUBSTR, CONCAT / `||`, REPLACE, TRIM, LEFT, RIGHT | ✅ |
| Zahlenfunktionen | ROUND, ABS, CEIL/FLOOR (MySQL), Modulo `%` | ✅ |
| Datumsfunktionen | YEAR, MONTH, DAY, CURDATE/NOW, DATEDIFF, (SQLite: strftime, date) | ✅ |
| NULL-Funktionen | COALESCE, IFNULL, NULLIF | ✅ |
| CAST | Typumwandlung | ✅ |
| Mengenoperationen | UNION, UNION ALL, INTERSECT, EXCEPT | ✅ |
| VIEWs | CREATE VIEW, Nutzen, DROP VIEW | ✅ |

## 7. Aggregations
| Thema | Inhalt | |
|---|---|---|
| Aggregatfunktionen | COUNT(*), COUNT(spalte), COUNT(DISTINCT), SUM, AVG, MIN, MAX | ✅ |
| NULL bei Aggregaten | NULL wird ignoriert | ✅ |
| GROUP BY | Eine und mehrere Spalten, Regel: jede Nicht-Aggregat-Spalte muss in GROUP BY | ✅ |
| HAVING | Gruppen filtern, WHERE vs. HAVING | ✅ |
| Ausführungsreihenfolge | FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT | ✅📖 |
| GROUP_CONCAT | Werte einer Gruppe zusammenfügen | ✅ |
| Bedingte Aggregation | `SUM(CASE WHEN ...)` | ✅ |
| Fensterfunktionen (Bonus) | ROW_NUMBER, RANK, DENSE_RANK, SUM() OVER (PARTITION BY) | ✅ |

## 8. Subqueries (Unterabfragen)
| Thema | Inhalt | |
|---|---|---|
| Skalare Unterabfrage | In WHERE (`> (SELECT AVG ...)`) und in SELECT | ✅ |
| IN / NOT IN | Listen-Unterabfrage, NULL-Falle bei NOT IN | ✅ |
| EXISTS / NOT EXISTS | Existenzprüfung | ✅ |
| Korrelierte Unterabfrage | Bezug auf äußere Zeile | ✅ |
| Unterabfrage in FROM | Abgeleitete Tabelle (Derived Table) | ✅ |
| ANY / ALL | Theorie (MySQL) + Alternativen | 📖 |
| CTE (WITH) | Lesbare Unterabfragen, rekursive CTE (Bonus) | ✅ |
| Unterabfragen in DML | `UPDATE/DELETE ... WHERE x IN (SELECT ...)` | ✅ |

## 9. Normalization (Normalisierung & Datenmodellierung)
| Thema | Inhalt | |
|---|---|---|
| Anomalien | Einfüge-, Änderungs-, Löschanomalie, Redundanz | 📖 |
| Schlüsselbegriffe | Superschlüssel, Schlüsselkandidat, Primär-, Fremd-, Surrogatschlüssel | 📖 |
| Funktionale Abhängigkeit | voll / partiell / transitiv | 📖 |
| 1. NF | Atomare Werte, keine Wiederholungsgruppen | 📖✅ |
| 2. NF | Keine partiellen Abhängigkeiten vom zusammengesetzten Schlüssel | 📖✅ |
| 3. NF | Keine transitiven Abhängigkeiten | 📖✅ |
| BCNF, Denormalisierung | Kurz: wann man bewusst denormalisiert | 📖 |
| Beziehungen | 1:1, 1:n, n:m (Zwischentabelle), Kardinalitäten, ERM → Relationenmodell | 📖✅ |
| Migration | Normalisierte Tabellen anlegen und mit `INSERT ... SELECT DISTINCT` befüllen | ✅ |

## 10. Joins
| Thema | Inhalt | |
|---|---|---|
| Grundidee | Kartesisches Produkt, Join-Bedingung | 📖 |
| INNER JOIN | ON, Tabellenaliase, mehrdeutige Spalten | ✅ |
| Mehrere Joins | 3+ Tabellen, n:m über `inventar` | ✅ |
| LEFT / RIGHT JOIN | Alle Zeilen einer Seite, NULL-Auffüllung | ✅ |
| Anti-Join | `LEFT JOIN ... WHERE rechts.id IS NULL` | ✅ |
| ON vs. WHERE | Filter beim LEFT JOIN richtig platzieren | ✅ |
| FULL OUTER JOIN | In MySQL über UNION nachbauen | ✅ |
| CROSS JOIN | Alle Kombinationen | ✅ |
| SELF JOIN | Tabelle mit sich selbst verbinden | ✅ |
| Join + Aggregation | GROUP BY über verbundene Tabellen, LEFT JOIN + COUNT | ✅ |
| Alte Syntax, USING, NATURAL | `FROM a, b WHERE ...`, `USING(spalte)` | 📖 |

## 11. Performance
| Thema | Inhalt | |
|---|---|---|
| Wie eine DB sucht | Full Table Scan vs. Index (B-Baum) | 📖 |
| CREATE INDEX | Normaler, UNIQUE, zusammengesetzter Index, DROP INDEX | ✅ |
| EXPLAIN | Ausführungsplan lesen (SQLite: EXPLAIN QUERY PLAN) | ✅ |
| Wann Index nicht greift | `LIKE '%x'`, Funktionen auf Spalten, Linkspräfix-Regel | ✅📖 |
| Kosten von Indizes | Langsamere INSERT/UPDATE, Speicher | 📖 |
| Gute Abfragen | Nur benötigte Spalten, früh filtern, LIMIT, EXISTS vs. IN, N+1 Problem | 📖 |
| Transaktionen & Sperren | ACID, Isolation (kurz), Batch-Inserts in Transaktion | 📖 |
| DCL & Sicherheit | GRANT, REVOKE, Benutzer, SQL-Injection & Prepared Statements | 📖 |

---

## Abdeckung der Lehrer-Dateien (DML-Ordner)
| Lehrer-Datei | Im Spiel |
|---|---|
| 01_Insert | Kapitel 4 |
| 02_Select | Kapitel 1, 5, 6 |
| 03_Where | Kapitel 5 |
| 04_Like | Kapitel 5 |
| 05_Aggregatfunktionen | Kapitel 7 |
| 06_OrderBy_GroupBy_Having | Kapitel 6, 7 |
| 07_EinJoin / 08_Zwei_Joins / 09_Left_Right_Join | Kapitel 10 |
| 10_Delete / 11_Update | Kapitel 4 |

Was die Lehrer-Dateien **nicht** abdecken und hier ergänzt wird: komplette DDL, alle Constraints,
Transaktionen, NULL-Logik, CASE, Funktionen, Mengenoperationen, Views, Unterabfragen, CTEs,
Fensterfunktionen, Normalisierung, Self/Cross/Full Joins, Indizes und Performance.
