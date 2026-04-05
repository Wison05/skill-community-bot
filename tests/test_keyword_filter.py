import unittest

from filters import KeywordFilter


class KeywordFilterBehaviorTests(unittest.TestCase):
    def test_allows_high_intent_adk_agent_titles(self):
        filter_instance = KeywordFilter()
        post = {
            "title": "Deploying ADK Agents on Azure ACA (Azure Container Apps)",
            "summary": "",
            "tags": "gemini, azurecontainerapps, agents, googleadk",
        }

        is_relevant, score, matched_keywords = filter_instance.check_relevance(post)

        self.assertTrue(is_relevant)
        self.assertEqual(score, 1.0)
        self.assertIn("agent", matched_keywords)

    def test_allows_high_intent_agent_framework_titles(self):
        filter_instance = KeywordFilter()
        post = {
            "title": "microsoft /agent-framework",
            "summary": "A workflow toolkit for agent orchestration.",
            "tags": "Python",
        }

        is_relevant, score, _ = filter_instance.check_relevance(post)

        self.assertTrue(is_relevant)
        self.assertLess(score, 1.5)

    def test_rejects_generic_single_agent_mentions(self):
        filter_instance = KeywordFilter()
        post = {
            "title": "What every AI agent team gets wrong",
            "summary": "",
            "tags": "",
        }

        is_relevant, score, _ = filter_instance.check_relevance(post)

        self.assertFalse(is_relevant)
        self.assertEqual(score, 1.0)


if __name__ == "__main__":
    _ = unittest.main()
