import feedparser
from typing import Any, Dict, List

from collectors.base import BaseCollector


class PyTorchBlogCollector(BaseCollector):
    def __init__(self, max_posts: int = 10):
        super().__init__("PyTorch Blog", max_posts)
        self.rss_url = "https://pytorch.org/blog/feed/"

    @staticmethod
    def _format_tags(entry: Dict[str, Any]) -> str:
        return ", ".join(
            tag.get("term", "")
            for tag in entry.get("tags", [])
            if tag.get("term", "")
        )

    def collect(self) -> List[Dict[str, Any]]:
        try:
            feed = feedparser.parse(self.rss_url)
            posts = []

            for entry in feed.entries[: self.max_posts]:
                posts.append(
                    {
                        "source_name": self.source_name,
                        "title": entry.get("title", ""),
                        "url": entry.get("link", ""),
                        "summary": entry.get("summary", ""),
                        "tags": self._format_tags(entry),
                        "published_at": entry.get("published", ""),
                    }
                )

            return posts
        except Exception:
            return []
