import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from collectors.base import BaseCollector
from config import REDDIT_USER_AGENT

logger = logging.getLogger(__name__)


class RedditCollector(BaseCollector):
    def __init__(self, max_posts: int = 10, subreddits: Optional[List[str]] = None):
        super().__init__("Reddit", max_posts)
        self.subreddits = subreddits or [
            "programming",
            "webdev",
            "machinelearning",
            "artificial",
            "OpenAI",
            "ClaudeAI",
        ]
        self.headers = {"User-Agent": REDDIT_USER_AGENT}

    def collect(self) -> List[Dict[str, Any]]:
        all_posts: List[Dict[str, Any]] = []
        posts_per_subreddit = max(1, self.max_posts // len(self.subreddits))

        for subreddit_name in self.subreddits:
            try:
                posts = self._collect_from_subreddit(subreddit_name, posts_per_subreddit)
                all_posts.extend(posts)
                logger.info(f"Collected {len(posts)} posts from r/{subreddit_name}")
            except requests.RequestException as error:
                logger.error(f"Error collecting from r/{subreddit_name}: {error}")

        return all_posts[:self.max_posts]

    def _collect_from_subreddit(
        self, subreddit_name: str, limit: int
    ) -> List[Dict[str, Any]]:
        response = requests.get(
            f"https://www.reddit.com/r/{subreddit_name}/hot.json",
            headers=self.headers,
            params={"limit": limit + 5, "raw_json": 1},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        posts: List[Dict[str, Any]] = []
        for child in data.get("data", {}).get("children", []):
            post_data = child.get("data", {})
            if post_data.get("stickied"):
                continue

            published_at = self._format_published_at(post_data.get("created_utc"))
            posts.append(
                {
                    "source_name": self.source_name,
                    "title": post_data.get("title", ""),
                    "url": f"https://reddit.com{post_data.get('permalink', '')}",
                    "summary": (post_data.get("selftext") or "")[:500],
                    "tags": subreddit_name,
                    "published_at": published_at,
                }
            )

            if len(posts) >= limit:
                break

        return posts

    @staticmethod
    def _format_published_at(created_utc: Any) -> str:
        if created_utc is None:
            return ""

        try:
            return datetime.utcfromtimestamp(float(created_utc)).isoformat()
        except (TypeError, ValueError, OSError):
            return ""
