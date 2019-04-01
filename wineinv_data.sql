--
-- File generated with SQLiteStudio v3.2.1 on Mon Apr 1 13:52:16 2019
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: userinventory
CREATE TABLE userinventory (
    wine_id     INTEGER,
    bottle_size VARCHAR,
    location    VARCHAR,
    date_in     STRING,
    date_out    STRING
);


-- Table: winedata
CREATE TABLE winedata (
    wine_id  INTEGER      UNIQUE ON CONFLICT ROLLBACK
                          PRIMARY KEY ASC ON CONFLICT ROLLBACK,
    upc      INTEGER,
    winery   STRING,
    region   STRING,
    name     STRING,
    varietal STRING,
    vintage  INTEGER,
    wtype    STRING,
    msrp     REAL (12, 2),
    value    REAL (12, 2),
    rating   STRING,
    comments STRING
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
