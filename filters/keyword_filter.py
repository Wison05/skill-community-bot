from typing import List, Dict, Any, Tuple
from config import SKILL_KEYWORDS, RELATED_KEYWORDS


class KeywordFilter:
    def __init__(
        self,
        skill_keywords: List[str] = None,
        related_keywords: List[str] = None,
    ):
        self.skill_keywords = [k.lower() for k in (skill_keywords or SKILL_KEYWORDS)]
        self.related_keywords = [k.lower() for k in (related_keywords or RELATED_KEYWORDS)]

    def check_relevance(self, post: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
        title = post.get("title", "").lower()
        summary = post.get("summary", "").lower()
        tags = post.get("tags", "").lower()

        text = f"{title} {summary} {tags}"

        matched_keywords = []
        score = 0.0

        for keyword in self.skill_keywords:
            if keyword in text:
                matched_keywords.append(keyword)
                if keyword in title:
                    score += 3.0
                elif keyword in tags:
                    score += 2.0
                else:
                    score += 1.0

        for keyword in self.related_keywords:
            if keyword in text:
                matched_keywords.append(keyword)
                if keyword in title:
                    score += 1.5
                elif keyword in tags:
                    score += 1.0
                else:
                    score += 0.5

        is_relevant = score >= 2.0 or any(k in title for k in self.skill_keywords)

        return is_relevant, score, matched_keywords

    def filter_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        filtered = []
        for post in posts:
            is_relevant, score, matched = self.check_relevance(post)
            if is_relevant:
                post["relevance_score"] = score
                post["matched_keywords"] = ", ".join(matched)
                filtered.append(post)
        return filtered


class Deduplicator:
    def __init__(self):
        self.seen_urls = set()
        self.seen_titles = set()

    def is_duplicate(self, post: Dict[str, Any]) -> bool:
        url = post.get("url", "").lower().rstrip("/")
        title = post.get("title", "").lower().strip()

        if url in self.seen_urls:
            return True

        if title in self.seen_titles:
            return True

        return False

    def add(self, post: Dict[str, Any]):
        url = post.get("url", "").lower().rstrip("/")
        title = post.get("title", "").lower().strip()
        self.seen_urls.add(url)
        self.seen_titles.add(title)

    def deduplicate(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        unique = []
        for post in posts:
            if not self.is_duplicate(post):
                unique.append(post)
                self.add(post)
        return unique
