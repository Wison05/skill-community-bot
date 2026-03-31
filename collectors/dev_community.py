import requests
from typing import List, Dict, Any
from collectors.base import BaseCollector


class DevCommunityCollector(BaseCollector):
    def __init__(self, max_posts: int = 10):
        super().__init__("DEV Community", max_posts)
        self.base_url = "https://dev.to/api/articles"

    def collect(self) -> List[Dict[str, Any]]:
        try:
            response = requests.get(
                self.base_url,
                params={
                    "page": 1,
                    "per_page": self.max_posts,
                },
                timeout=30,
            )
            response.raise_for_status()
            articles = response.json()

            posts = []
            for article in articles:
                post = {
                    "source_name": self.source_name,
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "summary": article.get("description", ""),
                    "tags": ", ".join(article.get("tag_list", [])),
                    "published_at": article.get("published_at", ""),
                }
                posts.append(post)

            return posts
        except Exception:
            return []
