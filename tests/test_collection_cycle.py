import unittest

from main import SkillCommunityBot


class CollectAndFilterTests(unittest.IsolatedAsyncioTestCase):
    async def test_save_failures_do_not_increment_new_count(self):
        bot = SkillCommunityBot.__new__(SkillCommunityBot)
        setattr(bot, "collectors", [_FakeCollector()])
        setattr(bot, "db", _FakeCollectionDatabase())
        setattr(bot, "filter", _PassthroughFilter())

        new_count = await bot.collect_and_filter()

        self.assertEqual(new_count, 0)


class _FakeCollector:
    source_name = "Fake Source"

    def collect(self):
        return [
            {
                "source_name": self.source_name,
                "title": "Agent Framework Update",
                "url": "https://example.com/post",
                "summary": "",
                "tags": "",
                "published_at": "2026-04-05T01:00:00",
                "matched_keywords": "agent framework",
                "relevance_score": 1.5,
            }
        ]


class _FakeCollectionDatabase:
    def get_recent_posts(self, hours: int = 48):
        return []

    def post_exists(self, url: str):
        return False

    def save_post(self, **kwargs):
        return False


class _PassthroughFilter:
    def filter_posts(self, posts):
        return posts


if __name__ == "__main__":
    _ = unittest.main()
