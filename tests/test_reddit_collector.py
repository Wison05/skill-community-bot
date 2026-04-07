import unittest
from unittest.mock import Mock, patch

import requests

from collectors.reddit import RedditCollector


class RedditCollectorTests(unittest.TestCase):
    @patch("requests.get")
    def test_collect_uses_public_json_and_skips_stickied_posts(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "data": {
                "children": [
                    {
                        "data": {
                            "stickied": True,
                            "title": "Pinned Post",
                            "permalink": "/r/programming/comments/pinned/post/",
                            "selftext": "",
                            "created_utc": 1712400000,
                        }
                    },
                    {
                        "data": {
                            "stickied": False,
                            "title": "Agent framework launch",
                            "permalink": "/r/programming/comments/abc123/agent_framework_launch/",
                            "selftext": "workflow toolkit",
                            "created_utc": 1712400300,
                        }
                    },
                ]
            }
        }
        mock_get.return_value = response

        collector = RedditCollector(max_posts=2, subreddits=["programming"])

        posts = collector.collect()

        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["title"], "Agent framework launch")
        self.assertEqual(
            posts[0]["url"],
            "https://reddit.com/r/programming/comments/abc123/agent_framework_launch/",
        )
        self.assertEqual(posts[0]["tags"], "programming")
        self.assertTrue(posts[0]["published_at"])
        mock_get.assert_called_once()
        self.assertEqual(
            mock_get.call_args.kwargs["params"],
            {"limit": 7, "raw_json": 1},
        )

    @patch("requests.get")
    def test_collect_returns_empty_list_when_request_fails(self, mock_get):
        mock_get.side_effect = requests.RequestException("boom")

        collector = RedditCollector(max_posts=3, subreddits=["programming"])

        posts = collector.collect()

        self.assertEqual(posts, [])


if __name__ == "__main__":
    _ = unittest.main()
