BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Subsections" (
	"id"	INTEGER,
	"id_sections"	INTEGER,
	"title"	TEXT,
	PRIMARY KEY("id"),
	FOREIGN KEY("id_sections") REFERENCES "Sections"("id")
);
CREATE TABLE IF NOT EXISTS "Steps" (
	"id"	INTEGER,
	"id_subsections"	INTEGER,
	"title"	TEXT,
	"defenition"	TEXT,
	"image"	BLOB,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "printers" (
	"id"	INTEGER,
	"model"	TEXT,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "Sections" (
	"id"	INTEGER,
	"text"	TEXT,
	"id_model"	INTEGER,
	PRIMARY KEY("id")
);
COMMIT;
