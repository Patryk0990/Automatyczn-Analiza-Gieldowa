CREATE TABLE IF NOT EXISTS users_api_settings (
    "id" serial PRIMARY KEY,
    "user_id" integer NOT NULL,
    "apca_api_key_id" varchar(256),
    "apca_api_secret_key" varchar(256),
	CONSTRAINT user_id_fkey
		FOREIGN KEY(user_id) 
		REFERENCES users(id)
		ON DELETE CASCADE
);