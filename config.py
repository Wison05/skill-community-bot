import os
from typing import TypedDict

from dotenv import load_dotenv

_ = load_dotenv()

DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN") or ""
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))

COLLECTION_INTERVAL_HOURS = int(os.getenv("COLLECTION_INTERVAL_HOURS", "6"))
MAX_POSTS_PER_SOURCE = int(os.getenv("MAX_POSTS_PER_SOURCE", "10"))

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
    "mcp",
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
    x_twitter: SourceConfig
    hada_news: SourceConfig


SOURCES: SourcesConfig = {
    "dev_community": {
        "enabled": True,
        "url": "https://dev.to/api/articles",
        "max_posts": 10,
    },
    "hacker_news": {
        "enabled": True,
        "url": "https://hacker-news.firebaseio.com/v0",
        "max_posts": 10,
    },
    "github_trending": {
        "enabled": True,
        "url": "https://github.com/trending",
        "max_posts": 10,
    },
    "reddit": {
        "enabled": True,
        "url": "https://www.reddit.com",
        "max_posts": 10,
        "subreddits": ["programming", "webdev", "machinelearning", "artificial", "OpenAI", "ClaudeAI", "Python", "web_design"],
    },
    "x_twitter": {
        "enabled": True,
        "url": "https://x.com",
        "max_posts": 8,
    },
    "hada_news": {
        "enabled": True,
        "url": "https://news.hada.io/rss/news",
        "max_posts": 10,
    },
}
