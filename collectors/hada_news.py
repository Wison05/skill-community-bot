import feedparser
from typing import List, Dict, Any
from collectors.base import BaseCollector


class HadaNewsCollector(BaseCollector):
    def __init__(self, max_posts: int = 10):
        super().__init__("Hada News", max_posts)
        self.rss_url = "https://news.hada.io/rss/news"

    def collect(self) -> List[Dict[str, Any]]:
        try:
            feed = feedparser.parse(self.rss_url)
            posts = []

            for entry in feed.entries[: self.max_posts]:
                post = {
                    "source_name": self.source_name,
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "tags": "",
                    "published_at": entry.get("published", ""),
                }
                posts.append(post)

            return posts
        except Exception:
            return []
