"""Kontrollabfragen, die in mehreren Kapiteln gebraucht werden."""

_TYPKATEGORIE = """CASE
    WHEN upper(type) LIKE '%INT%' THEN 'Ganzzahl'
    WHEN upper(type) LIKE '%CHAR%' OR upper(type) LIKE '%TEXT%' OR upper(type) LIKE '%CLOB%' THEN 'Text'
    WHEN upper(type) LIKE '%DEC%' OR upper(type) LIKE '%NUM%' OR upper(type) LIKE '%REAL%'
      OR upper(type) LIKE '%FLOA%' OR upper(type) LIKE '%DOUB%' THEN 'Kommazahl'
    WHEN upper(type) LIKE '%DATE%' OR upper(type) LIKE '%TIME%' THEN 'Datum/Zeit'
    WHEN upper(type) LIKE '%BOOL%' THEN 'Boolean'
    ELSE type END"""


def spalten(tabelle):
    """Spaltennamen + grobe Typ-Kategorie in Tabellenreihenfolge."""
    return f"SELECT name AS spalte, {_TYPKATEGORIE} AS typ FROM pragma_table_info('{tabelle}') ORDER BY cid"


def spaltennamen(tabelle):
    return f"SELECT name AS spalte FROM pragma_table_info('{tabelle}') ORDER BY cid"


TABELLEN = "SELECT name AS tabelle FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
VIEWS = "SELECT name AS view FROM sqlite_master WHERE type = 'view' ORDER BY name"


def indizes(tabelle):
    """Selbst angelegte Indizes einer Tabelle (Spalten + unique), ohne Index-Namen."""
    return (f"SELECT group_concat(ii.name, ',' ORDER BY ii.seqno) AS spalten, il.\"unique\" AS eindeutig "
            f"FROM pragma_index_list('{tabelle}') il JOIN pragma_index_info(il.name) ii "
            f"WHERE il.origin = 'c' GROUP BY il.name ORDER BY spalten")
