from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseCollector(ABC):
    def __init__(self, source_name: str, max_posts: int = 10):
        self.source_name = source_name
        self.max_posts = max_posts

    @abstractmethod
    def collect(self) -> List[Dict[str, Any]]:
        pass

    def normalize_post(self, raw_post: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "source_name": self.source_name,
            "title": raw_post.get("title", ""),
            "url": raw_post.get("url", ""),
            "summary": raw_post.get("summary", ""),
            "tags": raw_post.get("tags", ""),
            "published_at": raw_post.get("published_at", ""),
        }
