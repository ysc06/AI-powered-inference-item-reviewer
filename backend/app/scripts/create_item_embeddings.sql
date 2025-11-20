CREATE TALBE IF NOT EXISTS item_embeddings(
    item_id     INTEGER PRIMARY KEY, 
    model       TEXT NOT NULL,
    embedding   BLOB NOT NULL,
    updated_at  TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(item_id) REFERENCES items(id) ON DELETE CASACDE
);