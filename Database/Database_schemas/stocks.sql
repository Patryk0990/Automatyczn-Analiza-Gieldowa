CREATE TABLE IF NOT EXISTS stocks(
    "id" serial PRIMARY KEY,
    "symbol" varchar(25) NOT NULL,
    "name" varchar(256) NOT NULL,
    "exchange" varchar(25)
);