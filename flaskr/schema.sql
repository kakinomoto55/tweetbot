DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS tweet_table;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE tweet_table (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  tw_type TEXT NOT NULL,
  tw_memo TEXT,
  tw_dow TEXT,
  tw_rdm TEXT NOT NULL,
  tw_time TEXT NOT NULL,
  weather_condition TEXT,
  temp_condition TEXT,
  tweet1 TEXT NOT NULL,
  tweet2 TEXT,
  tweet3 TEXT,
  tweet4 TEXT,
  tweet5 TEXT,
  tweet6 TEXT,
  tweet7 TEXT,
  tweet8 TEXT,
  tweet9 TEXT,
  tweet10 TEXT,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

