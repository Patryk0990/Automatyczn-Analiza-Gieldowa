CREATE TABLE IF NOT EXISTS users_interface_settings (
    "id" serial PRIMARY KEY,
    "user_id" integer NOT NULL,
    "dark_mode" BOOLEAN DEFAULT FALSE NOT NULL,
    "theme_mode" smallint DEFAULT 3 NOT NULL,
    "font_size" smallint DEFAULT 2 NOT NULL,
	CONSTRAINT user_id_fkey
		FOREIGN KEY(user_id) 
		REFERENCES users(id)
		ON DELETE CASCADE
);