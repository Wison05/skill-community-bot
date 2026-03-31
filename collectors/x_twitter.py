import requests
from typing import List, Dict, Any
from collectors.base import BaseCollector


class XCollector(BaseCollector):
    def __init__(self, max_posts: int = 10):
        super().__init__("X (Twitter)", max_posts)
        self.search_queries = [
            "skill AI agent",
            "developer skill",
            "AI skill marketplace",
            "prompt skill",
        ]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0"
        }

    def collect(self) -> List[Dict[str, Any]]:
        all_posts = []
        posts_per_query = max(1, self.max_posts // len(self.search_queries))

        for query in self.search_queries:
            try:
                posts = self._search_tweets(query, posts_per_query)
                all_posts.extend(posts)
            except Exception:
                continue

        return all_posts[:self.max_posts]

    def _search_tweets(self, query: str, limit: int) -> List[Dict[str, Any]]:
        url = "https://nitter.net/search"
        
        response = requests.get(
            url,
            headers=self.headers,
            params={"f": "tweets", "q": query},
            timeout=30,
        )
        response.raise_for_status()

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        
        tweets = soup.find_all("div", class_="timeline-item", limit=limit)
        
        posts = []
        for tweet in tweets:
            try:
                link_elem = tweet.find("a", class_="tweet-link")
                if not link_elem:
                    continue
                
                tweet_url = link_elem.get("href", "")
                if tweet_url.startswith("/"):
                    tweet_url = f"https://nitter.net{tweet_url}"
                
                content_elem = tweet.find("div", class_="tweet-content")
                content = content_elem.get_text(strip=True) if content_elem else ""
                
                username_elem = tweet.find("a", class_="username")
                username = username_elem.get_text(strip=True) if username_elem else "unknown"
                
                post = {
                    "source_name": self.source_name,
                    "title": f"@{username}: {content[:100]}...",
                    "url": tweet_url.replace("nitter.net", "x.com"),
                    "summary": content[:500],
                    "tags": "twitter",
                    "published_at": "",
                }
                posts.append(post)
            except Exception:
                continue

        return posts
