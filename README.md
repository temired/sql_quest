# SQL-Quest ⚔️

Ein Lernspiel, das dir SQL komplett beibringt – von `SELECT *` bis zu Indizes und Normalisierung.
Gespielt wird in der RPG-Spielwelt aus dem Unterricht (gilden, spieler, gegenstaende, inventar, monster, quests).

## Herunterladen & Starten
Voraussetzung: [Python 3.12 oder neuer](https://www.python.org/downloads/) (unter Windows bei der Installation „Add Python to PATH“ anhaken).

1. Herunterladen – entweder oben auf **Code → Download ZIP** klicken und entpacken, oder:
   ```
   git clone https://github.com/temired/sql_quest.git
   ```
2. Starten – such dir aus, wie du spielen willst (beide nutzen denselben Spielstand):

   | | Windows | Terminal |
   |---|---|---|
   | 🖥️ **Mit Oberfläche** (Aufgabe links, SQL-Editor rechts) | Doppelklick auf `start_web.bat` | `python web.py` |
   | ⌨️ **Im Terminal** | Doppelklick auf `start.bat` | `python spielen.py` |

   Die Oberfläche öffnet sich im Browser, läuft aber komplett lokal auf deinem Rechner (auch ohne Internet).
   Das schwarze Fenster dabei offen lassen – zum Beenden schließen oder Strg+C.

Sonst ist nichts zu installieren, und eine MySQL-Verbindung ist nicht nötig – das Spiel nutzt SQLite,
das in Python eingebaut ist, und versteht die wichtigsten MySQL-Schreibweisen
(`AUTO_INCREMENT`, `SHOW TABLES`, `DESCRIBE`, `YEAR()`, `CONCAT()`, `LIMIT 10, 5`, `GROUP_CONCAT(... SEPARATOR ...)`, `ENUM`, `TRUNCATE` ...).

## Spielstand
Dein Fortschritt wird automatisch nach jeder gelösten Aufgabe in `fortschritt.json` gespeichert –
im Spielordner, auf deinem Rechner. Nach dem Beenden oder einem Neustart des PCs geht es genau dort weiter.
- Die Datei wird **nicht** auf GitHub hochgeladen (steht in `.gitignore`) – jeder hat seinen eigenen Spielstand.
- Lädst du das Spiel neu herunter, kopiere deine alte `fortschritt.json` (und `sandbox.db`) in den neuen Ordner.
- Neu anfangen: im Terminal-Hauptmenü **R** oder in der Oberfläche über ⚔️ SQL-Quest → „Fortschritt zurücksetzen“.

## So funktioniert's
- 11 Kapitel, jedes mit Lektionen (Theorie → Aufgaben) und einem **Bosskampf**.
- Du tippst SQL, das Spiel führt es auf einer frischen Datenbank aus und vergleicht das **Ergebnis**
  mit der Musterlösung. Es zählt also jede richtige Lösung, nicht nur genau eine Schreibweise.
- XP sammeln, Ränge aufsteigen. Hinweise kosten ein paar XP, die Musterlösung fast alle.

**In der Oberfläche:** `Strg+Enter` führt aus, `Strg+Shift+Enter` gibt ab, `Strg+/` kommentiert Zeilen aus.
Links gibt es die Reiter Aufgabe, Theorie und Tabellen (Klick auf einen Spaltennamen fügt ihn in den Editor ein),
unten rechts Ergebnis, Erwartet und Lösung. Mit 🧪 Sandbox kannst du frei üben, ⚔️ SQL-Quest öffnet die Kapitelübersicht.

**Im Terminal:**

| Befehl | Wirkung |
|---|---|
| `.h` | Hinweis |
| `.e` | erwartetes Ergebnis anzeigen |
| `.l` | Musterlösung |
| `.t` / `.s spieler` | Tabellen / Struktur einer Tabelle |
| `.p SELECT ...` | etwas ausprobieren, ohne es abzugeben |
| `.d` | Inhalt von `antwort.sql` abgeben (für lange Befehle im Editor) |
| `.theorie` | Theorie nochmal |
| `.w` / `.m` | Aufgabe überspringen / Menü |

## Dateien
| Datei | Zweck |
|---|---|
| `LEHRPLAN.md` | Was in welchem Kapitel drankommt (vollständige Themenliste) |
| `SPICKZETTEL.md` | Alle Befehle kompakt zum Nachschlagen |
| `antwort.sql` | Dein Notizblock für lange Abfragen → im Spiel `.d` |
| `sandbox.db` | Deine freie Spielwiese (Menü → S), bleibt gespeichert |
| `fortschritt.json` | Dein Spielstand |
| `daten/welt.sql` | Die Spielwelt (Daten des Lehrers + 3 gildenlose Spieler, 1 Gegenstand ohne Wert, 1 Quest ohne Monster für NULL-Übungen) |
| `web.py`, `web/` | Die Oberfläche (lokaler Mini-Server + Webseite, nur Python-Standardbibliothek) |
| `test_loesungen.py` | Selbsttest: prüft, dass alle Musterlösungen funktionieren |

## Unterschiede zu MySQL, die du kennen solltest
Im Spiel stehen sie als lila **MySQL ▸** Hinweise direkt in der Theorie. Die wichtigsten:
`7 / 2` ist hier `3` (MySQL: `3.5`), `ALTER TABLE ... MODIFY` gibt es nicht, und `||` ist in MySQL ein ODER (dort `CONCAT` benutzen).
