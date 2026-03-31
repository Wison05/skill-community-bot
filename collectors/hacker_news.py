import requests
from typing import List, Dict, Any
from collectors.base import BaseCollector


class HackerNewsCollector(BaseCollector):
    def __init__(self, max_posts: int = 10):
        super().__init__("Hacker News", max_posts)
        self.base_url = "https://hacker-news.firebaseio.com/v0"

    def collect(self) -> List[Dict[str, Any]]:
        try:
            top_ids = self._get_top_story_ids()
            if not top_ids:
                return []

            posts = []
            for story_id in top_ids[: self.max_posts]:
                story = self._get_story(story_id)
                if story:
                    post = {
                        "source_name": self.source_name,
                        "title": story.get("title", ""),
                        "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                        "summary": "",
                        "tags": "",
                        "published_at": "",
                    }
                    posts.append(post)

            return posts
        except Exception:
            return []

    def _get_top_story_ids(self) -> List[int]:
        try:
            response = requests.get(
                f"{self.base_url}/topstories.json",
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return []

    def _get_story(self, story_id: int) -> Dict[str, Any]:
        try:
            response = requests.get(
                f"{self.base_url}/item/{story_id}.json",
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return {}
