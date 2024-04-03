---- CREATE TABLES ----

CREATE TABLE branch (
 url VARCHAR PRIMARY KEY,
 ip VARCHAR
);

CREATE TABLE customer (
 id INTEGER PRIMARY KEY,
 forename VARCHAR(20),
 surname VARCHAR(40),
 email VARCHAR(100),
 allergies VARCHAR(10)
);