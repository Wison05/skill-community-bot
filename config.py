import os
from typing import Optional, TypedDict

from dotenv import load_dotenv

_ = load_dotenv()


def _get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default

    return int(value)


def _get_float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default

    return float(value)


def _get_optional_int_env(name: str) -> Optional[int]:
    value = os.getenv(name)
    if value is None:
        return None

    return int(value)


def _source_max_posts(default: int) -> int:
    if MAX_POSTS_PER_SOURCE is not None:
        return MAX_POSTS_PER_SOURCE

    return default

DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN") or ""
DISCORD_CHANNEL_ID = _get_int_env("DISCORD_CHANNEL_ID", 0)

REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT") or "SkillCommunityBot/1.0"

COLLECTION_INTERVAL_HOURS = _get_float_env("COLLECTION_INTERVAL_HOURS", 0.5)
MAX_POSTS_PER_SOURCE = _get_optional_int_env("MAX_POSTS_PER_SOURCE")

DATABASE_PATH = os.getenv("DATABASE_PATH", "data/skill_bot.db")
SKILL_KEYWORDS = [
    "skill",
    "skills",
    "agent skill",
    "AI skill",
    "developer skill",
    "prompt skill",
    "marketplace skill",
    "reusable skill",
    "skill library",
    "skill system",
]

RELATED_KEYWORDS = [
    "agent",
    "workflow",
    "automation",
    "prompt",
    "template",
    "library",
    "tooling",
    "reusable",
    "MCP",
    "model context protocol",
]

STRONG_TITLE_KEYWORDS = [
    "adk agents",
    "adk agent",
    "agent framework",
    "model context protocol",
]


class SourceConfig(TypedDict):
    enabled: bool
    url: str
    max_posts: int


class RedditSourceConfig(SourceConfig):
    subreddits: list[str]


class SourcesConfig(TypedDict):
    dev_community: SourceConfig
    hacker_news: SourceConfig
    github_trending: SourceConfig
    reddit: RedditSourceConfig
    hada_news: SourceConfig


SOURCES: SourcesConfig = {
    "dev_community": {
        "enabled": True,
        "url": "https://dev.to/api/articles",
        "max_posts": _source_max_posts(10),
    },
    "hacker_news": {
        "enabled": True,
        "url": "https://hacker-news.firebaseio.com/v0",
        "max_posts": _source_max_posts(10),
    },
    "github_trending": {
        "enabled": True,
        "url": "https://github.com/trending",
        "max_posts": _source_max_posts(10),
    },
    "reddit": {
        "enabled": True,
        "url": "https://www.reddit.com",
        "max_posts": _source_max_posts(10),
        "subreddits": ["programming", "webdev", "machinelearning", "artificial", "OpenAI", "ClaudeAI", "Python", "web_design"],
    },
    "hada_news": {
        "enabled": True,
        "url": "https://news.hada.io/rss/news",
        "max_posts": _source_max_posts(10),
    },
}
