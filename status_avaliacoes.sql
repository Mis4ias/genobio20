PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "user_status_avaliacoes" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "tipo" varchar(30) NOT NULL);
INSERT INTO user_status_avaliacoes VALUES(1,'Submitted');
INSERT INTO user_status_avaliacoes VALUES(2,'Approved');
INSERT INTO user_status_avaliacoes VALUES(3,'Awaiting adjustment');
INSERT INTO user_status_avaliacoes VALUES(4,'Rejected');
COMMIT;
