-- SQL schema for PyStump
-- Designed for sqlite3

-- Announcements table
DROP TABLE IF EXISTS announcements;

CREATE TABLE IF NOT EXISTS announcements (
       id    	   INTEGER PRIMARY KEY AUTOINCREMENT
       ,title 	   TEXT NOT NULL
       ,content	   TEXT
       ,author	   TEXT
       ,activate   DATETIME
       ,expire	   DATETIME
       ,duration   INTEGER
       ,updated	   DATETIME
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
       	SELECT * FROM announcements
	WHERE (activate is NULL or activate = '' or activate < datetime('now')) AND
	      (expire is NULL or expire = '' or expire > datetime('now'))
	ORDER BY id ASC
;
