CREATE TABLE IF NOT EXISTS users(
    "id" serial PRIMARY KEY,
    "email" varchar(256) NOT NULL,
    "username" varchar(32) NOT NULL,
    "password" varchar(256) NOT NULL,
    "permission_level" smallint DEFAULT 0 NOT NULL,
    "active" BOOLEAN DEFAULT TRUE NOT NULL
);