import unittest
from unittest.mock import Mock, patch

from collectors.pytorch_blog import PyTorchBlogCollector


class PyTorchBlogCollectorTests(unittest.TestCase):
    @patch("feedparser.parse")
    def test_collect_reads_pytorch_blog_feed(self, mock_parse):
        mock_parse.return_value = Mock(
            entries=[
                {
                    "title": "Agent workflows with PyTorch",
                    "link": "https://pytorch.org/blog/agent-workflows/",
                    "summary": "A workflow update for PyTorch users.",
                    "published": "Fri, 19 Jun 2026 11:23:56 +0000",
                    "tags": [{"term": "Announcements"}, {"term": "Blog"}],
                },
                {
                    "title": "Second PyTorch post",
                    "link": "https://pytorch.org/blog/second/",
                    "summary": "Second summary.",
                    "published": "Thu, 18 Jun 2026 14:02:02 +0000",
                    "tags": [{"term": "Blog"}],
                },
            ]
        )

        collector = PyTorchBlogCollector(max_posts=1)

        posts = collector.collect()

        self.assertEqual(
            posts,
            [
                {
                    "source_name": "PyTorch Blog",
                    "title": "Agent workflows with PyTorch",
                    "url": "https://pytorch.org/blog/agent-workflows/",
                    "summary": "A workflow update for PyTorch users.",
                    "tags": "Announcements, Blog",
                    "published_at": "Fri, 19 Jun 2026 11:23:56 +0000",
                }
            ],
        )
        mock_parse.assert_called_once_with("https://pytorch.org/blog/feed/")

    @patch("feedparser.parse")
    def test_collect_returns_empty_list_when_feed_parse_fails(self, mock_parse):
        mock_parse.side_effect = RuntimeError("boom")

        collector = PyTorchBlogCollector(max_posts=3)

        self.assertEqual(collector.collect(), [])


if __name__ == "__main__":
    unittest.main()
