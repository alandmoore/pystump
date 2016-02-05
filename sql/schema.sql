-- SQL schema for PyStump
-- Designed for sqlite3

-- Announcements table
DROP TABLE IF EXISTS announcements;

CREATE TABLE IF NOT EXISTS announcements (
       id          INTEGER PRIMARY KEY AUTOINCREMENT
       ,title      TEXT NOT NULL
       ,content    TEXT
       ,author     TEXT
       ,activate   TIMESTAMP
       ,expire     TIMESTAMP
       ,duration   INTEGER
       ,updated    TIMESTAMP
       ,fg_color   TEXT
       ,bg_color   TEXT
);

-- Settings table
DROP TABLE IF EXISTS settings;

CREATE TABLE IF NOT EXISTS settings (
       setting_name TEXT PRIMARY KEY
       ,setting_value TEXT
       ,setting_type TEXT
);

-- Active announcements
DROP VIEW IF EXISTS announcements_v;

CREATE VIEW announcements_v AS
        SELECT *, (activate is NOT NULL AND activate != '' AND activate > datetime('now')) as delayed,
        (expire is NOT NULL AND expire != '' AND expire < datetime('now')) as expired
    FROM announcements
    ORDER BY id ASC
;
