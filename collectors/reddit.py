import requests
from typing import Any, Dict, List, Optional
from collectors.base import BaseCollector


class RedditCollector(BaseCollector):
    def __init__(self, max_posts: int = 10, subreddits: Optional[List[str]] = None):
        super().__init__("Reddit", max_posts)
        self.subreddits = subreddits or ["programming", "webdev", "machinelearning", "artificial", "OpenAI", "ClaudeAI"]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0"
        }

    def collect(self) -> List[Dict[str, Any]]:
        all_posts = []
        posts_per_subreddit = max(1, self.max_posts // len(self.subreddits))

        for subreddit in self.subreddits:
            try:
                posts = self._collect_from_subreddit(subreddit, posts_per_subreddit)
                all_posts.extend(posts)
            except Exception:
                continue

        return all_posts[:self.max_posts]

    def _collect_from_subreddit(self, subreddit: str, limit: int) -> List[Dict[str, Any]]:
        url = f"https://www.reddit.com/r/{subreddit}/hot.json"
        
        response = requests.get(
            url,
            headers=self.headers,
            params={"limit": limit},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        posts = []
        for child in data.get("data", {}).get("children", []):
            post_data = child.get("data", {})
            
            if post_data.get("stickied"):
                continue

            post = {
                "source_name": self.source_name,
                "title": post_data.get("title", ""),
                "url": f"https://reddit.com{post_data.get('permalink', '')}",
                "summary": post_data.get("selftext", "")[:500],
                "tags": subreddit,
                "published_at": "",
            }
            posts.append(post)

        return posts
