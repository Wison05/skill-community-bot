import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from collectors.base import BaseCollector


class GitHubTrendingCollector(BaseCollector):
    def __init__(self, max_posts: int = 10):
        super().__init__("GitHub Trending", max_posts)
        self.base_url = "https://github.com/trending"

    def collect(self) -> List[Dict[str, Any]]:
        try:
            response = requests.get(
                self.base_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0"
                },
                timeout=30,
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all("article", class_="Box-row", limit=self.max_posts)

            posts = []
            for article in articles:
                try:
                    link_elem = article.find("h2", class_="h3") or article.find("h2")
                    if not link_elem:
                        continue

                    a_tag = link_elem.find("a")
                    if not a_tag:
                        continue

                    href = a_tag.get("href", "")
                    if not href:
                        continue

                    title = a_tag.get_text(strip=True).replace("\n", " ").replace("  ", " ")
                    url = f"https://github.com{href}"

                    desc_elem = article.find("p", class_="col-9")
                    summary = desc_elem.get_text(strip=True) if desc_elem else ""

                    lang_elem = article.find("span", itemprop="programmingLanguage")
                    tags = lang_elem.get_text(strip=True) if lang_elem else ""

                    post = {
                        "title": title,
                        "url": url,
                        "summary": summary,
                        "tags": tags,
                        "published_at": "",
                    }
                    posts.append(post)
                except Exception:
                    continue

            return posts
        except Exception:
            return []
