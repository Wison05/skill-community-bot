import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
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

SOURCES = {
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
}
