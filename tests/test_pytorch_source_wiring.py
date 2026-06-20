import unittest

from collectors.pytorch_blog import PyTorchBlogCollector
from config import SOURCES
from main import SkillCommunityBot


class PyTorchSourceWiringTests(unittest.TestCase):
    def test_config_exposes_enabled_pytorch_blog_source(self):
        self.assertIn("pytorch_blog", SOURCES)
        self.assertTrue(SOURCES["pytorch_blog"]["enabled"])
        self.assertEqual(SOURCES["pytorch_blog"]["url"], "https://pytorch.org/blog/feed/")
        self.assertEqual(SOURCES["pytorch_blog"]["max_posts"], 10)

    def test_bot_initializes_pytorch_blog_collector(self):
        bot = SkillCommunityBot.__new__(SkillCommunityBot)

        collectors = bot._init_collectors()

        self.assertTrue(
            any(isinstance(collector, PyTorchBlogCollector) for collector in collectors)
        )


if __name__ == "__main__":
    unittest.main()
