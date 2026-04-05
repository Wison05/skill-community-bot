import os
import sqlite3
import tempfile
import unittest

from database import Database


class DatabaseMigrationTests(unittest.TestCase):
    def test_legacy_posts_table_migrates_before_new_index_usage(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "legacy.db")
            with sqlite3.connect(db_path) as conn:
                conn.executescript(
                    """
                    CREATE TABLE posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_name TEXT NOT NULL,
                        title TEXT NOT NULL,
                        url TEXT NOT NULL UNIQUE,
                        summary TEXT,
                        tags TEXT,
                        published_at TEXT,
                        matched_keywords TEXT,
                        relevance_score REAL DEFAULT 0,
                        sent BOOLEAN DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE INDEX idx_posts_url ON posts(url);
                    CREATE INDEX idx_posts_source ON posts(source_name);
                    CREATE INDEX idx_posts_sent ON posts(sent);
                    """
                )

            migrated_db = Database(db_path=db_path)

            with migrated_db.get_connection() as conn:
                column_names = {
                    row[1] for row in conn.execute("PRAGMA table_info(posts)").fetchall()
                }
                index_names = {
                    row[1] for row in conn.execute("PRAGMA index_list(posts)").fetchall()
                }

            self.assertIn("notification_status", column_names)
            self.assertIn("notification_claimed_at", column_names)
            self.assertIn("notification_error", column_names)
            self.assertIn("discord_message_id", column_names)
            self.assertIn("idx_posts_notification_status", index_names)


if __name__ == "__main__":
    _ = unittest.main()
