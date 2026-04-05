import unittest
from typing import Any, Optional

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
        notifier = _FakeNotifier(send_result=None)
        setattr(bot, "db", db)
        setattr(bot, "notifier", notifier)

        sent_count = await bot.send_notifications()

        self.assertEqual(sent_count, 0)
        self.assertEqual(db.marked_ids, [])
        self.assertEqual(db.failed_ids, [1])

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
        notifier = _FakeNotifier(send_result="discord-message-2")
        setattr(bot, "db", db)
        setattr(bot, "notifier", notifier)

        sent_count = await bot.send_notifications()

        self.assertEqual(sent_count, 1)
        self.assertEqual(db.marked_ids, [(2, "discord-message-2")])

    async def test_successful_send_with_finalize_failure_is_not_retried(self):
        bot = SkillCommunityBot.__new__(SkillCommunityBot)
        db = _FakeDatabase(
            [
                {
                    "id": 3,
                    "title": "Agent Framework Update",
                    "url": "https://example.com/post-3",
                }
            ],
            fail_mark_as_sent=True,
        )
        notifier = _FakeNotifier(send_result="discord-message-3")
        setattr(bot, "db", db)
        setattr(bot, "notifier", notifier)

        first_sent_count = await bot.send_notifications()
        second_sent_count = await bot.send_notifications()

        self.assertEqual(first_sent_count, 0)
        self.assertEqual(second_sent_count, 0)
        self.assertEqual(notifier.sent_posts, [3])
        self.assertEqual(db.sending_ids, [3])
        self.assertEqual(db.failed_ids, [])


class _FakeDatabase:
    def __init__(
        self,
        unsent_posts: list[dict[str, Any]],
        *,
        fail_mark_as_sent: bool = False,
    ):
        self.posts_by_id = {post["id"]: dict(post) for post in unsent_posts}
        self.status_by_id = {post["id"]: "pending" for post in unsent_posts}
        self.fail_mark_as_sent = fail_mark_as_sent
        self.sending_ids: list[int] = []
        self.marked_ids: list[tuple[int, str]] = []
        self.failed_ids: list[int] = []

    def get_unsent_posts(self):
        posts = []
        for post_id, status in self.status_by_id.items():
            if status in {"pending", "failed"}:
                posts.append(dict(self.posts_by_id[post_id]))
        return posts

    def mark_as_sending(self, post_id: int):
        if self.status_by_id[post_id] not in {"pending", "failed"}:
            return False

        self.status_by_id[post_id] = "sending"
        self.sending_ids.append(post_id)
        return True

    def mark_as_sent(self, post_id: int, discord_message_id: str):
        if self.fail_mark_as_sent:
            raise RuntimeError("database unavailable")

        self.status_by_id[post_id] = "sent"
        self.marked_ids.append((post_id, discord_message_id))
        return True

    def mark_as_failed(self, post_id: int, error_message: str):
        self.status_by_id[post_id] = "failed"
        self.failed_ids.append(post_id)
        return True


class _FakeNotifier:
    def __init__(self, send_result: Optional[str]):
        self.send_result = send_result
        self.sent_posts: list[int] = []

    async def send_post(self, post: dict[str, Any]):
        self.sent_posts.append(post["id"])
        return self.send_result


if __name__ == "__main__":
    _ = unittest.main()
