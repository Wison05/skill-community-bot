import unittest
from typing import Any

from main import SkillCommunityBot


class SendNotificationsTests(unittest.IsolatedAsyncioTestCase):
    async def test_failed_send_does_not_mark_post_as_sent(self):
        bot = SkillCommunityBot.__new__(SkillCommunityBot)
        db = _FakeDatabase(
            [
                {
                    "id": 1,
                    "title": "Agent Framework Update",
                    "url": "https://example.com/post",
                }
            ]
        )
        notifier = _FakeNotifier(send_result=False)
        setattr(bot, "db", db)
        setattr(bot, "notifier", notifier)

        sent_count = await bot.send_notifications()

        self.assertEqual(sent_count, 0)
        self.assertEqual(db.marked_ids, [])

    async def test_successful_send_marks_post_as_sent(self):
        bot = SkillCommunityBot.__new__(SkillCommunityBot)
        db = _FakeDatabase(
            [
                {
                    "id": 2,
                    "title": "ADK Agents on Azure",
                    "url": "https://example.com/post-2",
                }
            ]
        )
        notifier = _FakeNotifier(send_result=True)
        setattr(bot, "db", db)
        setattr(bot, "notifier", notifier)

        sent_count = await bot.send_notifications()

        self.assertEqual(sent_count, 1)
        self.assertEqual(db.marked_ids, [2])


class _FakeDatabase:
    def __init__(self, unsent_posts: list[dict[str, Any]]):
        self.unsent_posts = unsent_posts
        self.marked_ids: list[int] = []

    def get_unsent_posts(self):
        return list(self.unsent_posts)

    def mark_as_sent(self, post_id: int):
        self.marked_ids.append(post_id)


class _FakeNotifier:
    def __init__(self, send_result: bool):
        self.send_result = send_result

    async def send_post(self, post: dict[str, Any]):
        return self.send_result


if __name__ == "__main__":
    _ = unittest.main()
