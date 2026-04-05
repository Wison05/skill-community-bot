import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from config import SKILL_KEYWORDS, RELATED_KEYWORDS, STRONG_TITLE_KEYWORDS


class KeywordFilter:
    def __init__(
        self,
        skill_keywords: Optional[List[str]] = None,
        related_keywords: Optional[List[str]] = None,
        strong_title_keywords: Optional[List[str]] = None,
        min_score: float = 1.5,
    ):
        self.skill_keywords = [k.lower() for k in (skill_keywords or SKILL_KEYWORDS)]
        self.related_keywords = [k.lower() for k in (related_keywords or RELATED_KEYWORDS)]
        self.strong_title_keywords = [
            self._normalize_text(k) for k in (strong_title_keywords or STRONG_TITLE_KEYWORDS)
        ]
        self.min_score = min_score

    @staticmethod
    def _unique_keywords(keywords: List[str]) -> List[str]:
        unique_keywords: List[str] = []
        for keyword in keywords:
            if keyword not in unique_keywords:
                unique_keywords.append(keyword)

        return unique_keywords

    @staticmethod
    def _normalize_text(value: str) -> str:
        lowered = value.lower()
        normalized = re.sub(r"[^a-z0-9]+", " ", lowered)
        return " ".join(normalized.split())

    def check_relevance(self, post: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
        title = post.get("title", "").lower()
        summary = post.get("summary", "").lower()
        tags = post.get("tags", "").lower()
        normalized_title = self._normalize_text(post.get("title", ""))

        matched_keywords = []
        score = 0.0

        for keyword in self.skill_keywords:
            if keyword in title:
                matched_keywords.append(keyword)
                score += 3.0
            elif keyword in tags:
                matched_keywords.append(keyword)
                score += 2.0
            elif keyword in summary:
                matched_keywords.append(keyword)
                score += 1.0

        for keyword in self.related_keywords:
            if keyword in title:
                matched_keywords.append(keyword)
                score += 1.0
            elif keyword in tags:
                matched_keywords.append(keyword)
                score += 0.5
            elif keyword in summary:
                matched_keywords.append(keyword)
                score += 0.3

        strong_title_matches = [
            keyword for keyword in self.strong_title_keywords if keyword in normalized_title
        ]
        if strong_title_matches:
            matched_keywords.extend(strong_title_matches)
            score = max(score, self.min_score)

        title_has_skill = any(k in title for k in self.skill_keywords)
        title_has_strong_related = bool(strong_title_matches)
        is_relevant = score >= self.min_score or title_has_skill or title_has_strong_related

        return is_relevant, score, self._unique_keywords(matched_keywords)

    def filter_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        filtered = []
        for post in posts:
            is_relevant, score, matched = self.check_relevance(post)
            if is_relevant:
                post["relevance_score"] = score
                post["matched_keywords"] = ", ".join(self._unique_keywords(matched))
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


class TimeFilter:
    def __init__(self, days: int = 7):
        self.days = days
        self.cutoff_date = datetime.now() - timedelta(days=days)

    def is_recent(self, post: Dict[str, Any]) -> bool:
        published_at = post.get("published_at", "")
        if not published_at:
            return True

        try:
            if isinstance(published_at, str):
                if published_at.endswith("Z"):
                    published_at = published_at[:-1]
                pub_date = datetime.fromisoformat(published_at)
            else:
                return True
            return pub_date >= self.cutoff_date
        except (ValueError, TypeError):
            return True

    def filter_by_time(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [post for post in posts if self.is_recent(post)]
