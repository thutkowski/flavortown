DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE transactions (
    Date            TEXT,
    Desc            TEXT,
    Amount          REAL,
    TransactionType TEXT,
    Category        TEXT,
    Source          TEXT,
    CategoryStatus  TEXT,
    Week            INTEGER,
    Year            INTEGER
);


insert into transactions (Date,Desc,Amount,TransactionType,Category,Source,CategoryStatus,Week,Year) VALUES ("2024-07-30 00:00:00","Initial balance",912.28,"Debit","Financial","Ally","?",7,2024);

insert into transactions (Date,Desc,Amount,TransactionType,Category,Source,CategoryStatus,Week,Year) VALUES ("2024-01-01 00:00:00","Initial balance",1665.99,"Debit","Financial","ESL","?",1,2024);
