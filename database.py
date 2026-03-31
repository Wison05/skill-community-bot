import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from config import DATABASE_PATH


class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_tables()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_tables(self):
        with self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS posts (
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

                CREATE INDEX IF NOT EXISTS idx_posts_url ON posts(url);
                CREATE INDEX IF NOT EXISTS idx_posts_source ON posts(source_name);
                CREATE INDEX IF NOT EXISTS idx_posts_sent ON posts(sent);
            """)
            conn.commit()

    def save_post(
        self,
        source_name: str,
        title: str,
        url: str,
        summary: Optional[str] = None,
        tags: Optional[str] = None,
        published_at: Optional[str] = None,
        matched_keywords: Optional[str] = None,
        relevance_score: float = 0,
    ) -> bool:
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO posts 
                    (source_name, title, url, summary, tags, published_at, matched_keywords, relevance_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (source_name, title, url, summary, tags, published_at, matched_keywords, relevance_score),
                )
                conn.commit()
                return conn.total_changes > 0
        except sqlite3.Error:
            return False

    def post_exists(self, url: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT 1 FROM posts WHERE url = ?", (url,))
            return cursor.fetchone() is not None

    def get_unsent_posts(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM posts 
                WHERE sent = 0 
                ORDER BY relevance_score DESC, created_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def mark_as_sent(self, post_id: int):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE posts SET sent = 1 WHERE id = ?",
                (post_id,),
            )
            conn.commit()

    def get_recent_posts(self, hours: int = 24) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM posts 
                WHERE created_at >= datetime('now', '-{} hours')
                ORDER BY created_at DESC
                """.format(hours),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
            sent = conn.execute("SELECT COUNT(*) FROM posts WHERE sent = 1").fetchone()[0]
            unsent = conn.execute("SELECT COUNT(*) FROM posts WHERE sent = 0").fetchone()[0]
            return {
                "total": total,
                "sent": sent,
                "unsent": unsent,
            }
