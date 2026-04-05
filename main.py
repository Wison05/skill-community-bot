import asyncio
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from config import (
    DISCORD_BOT_TOKEN,
    DISCORD_CHANNEL_ID,
    COLLECTION_INTERVAL_HOURS,
    SOURCES,
)
from database import Database
from collectors import DevCommunityCollector, HackerNewsCollector, GitHubTrendingCollector, RedditCollector, XCollector, HadaNewsCollector
from filters import KeywordFilter, Deduplicator, TimeFilter
from notifier import DiscordNotifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_next_scheduled_time():
    now = datetime.now()
    # 30분 간격으로 스케줄링 (00분, 30분)
    if now.minute < 30:
        target = now.replace(minute=30, second=0, microsecond=0)
    else:
        target = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    return target


class SkillCommunityBot:
    def __init__(self):
        self.db = Database()
        self.filter = KeywordFilter()
        self.notifier = DiscordNotifier(DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID)
        self.collectors = self._init_collectors()
        self.running = False

    def _init_collectors(self):
        collectors = []
        if SOURCES["dev_community"]["enabled"]:
            collectors.append(
                DevCommunityCollector(SOURCES["dev_community"]["max_posts"])
            )
        if SOURCES["hacker_news"]["enabled"]:
            collectors.append(
                HackerNewsCollector(SOURCES["hacker_news"]["max_posts"])
            )
        if SOURCES["github_trending"]["enabled"]:
            collectors.append(
                GitHubTrendingCollector(SOURCES["github_trending"]["max_posts"])
            )
        if SOURCES["reddit"]["enabled"]:
            subreddits = SOURCES["reddit"].get("subreddits", ["programming"])
            collectors.append(
                RedditCollector(SOURCES["reddit"]["max_posts"], subreddits)
            )
        if SOURCES["x_twitter"]["enabled"]:
            collectors.append(
                XCollector(SOURCES["x_twitter"]["max_posts"])
            )
        if SOURCES["hada_news"]["enabled"]:
            collectors.append(
                HadaNewsCollector(SOURCES["hada_news"]["max_posts"])
            )
        return collectors

    def _collect_with_timeout(self, collector, timeout=20):
        try:
            posts = collector.collect()
            return posts
        except Exception as e:
            logger.error(f"Error collecting from {collector.source_name}: {e}")
            return []

    async def collect_and_filter(self):
        logger.info("Starting collection cycle...")

        all_posts = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self._collect_with_timeout, collector): collector
                for collector in self.collectors
            }
            
            for future in futures:
                collector = futures[future]
                try:
                    posts = future.result(timeout=25)
                    logger.info(f"Collected {len(posts)} posts from {collector.source_name}")
                    all_posts.extend(posts)
                except FutureTimeoutError:
                    logger.warning(f"Timeout collecting from {collector.source_name}")
                except Exception as e:
                    logger.error(f"Error collecting from {collector.source_name}: {e}")

        if not all_posts:
            logger.info("No posts collected")
            return 0

        time_filter = TimeFilter(days=14)
        recent_posts = time_filter.filter_by_time(all_posts)
        logger.info(f"After time filter (14 days): {len(recent_posts)} posts")

        deduplicator = Deduplicator()
        for existing_post in self.db.get_recent_posts(hours=48):
            deduplicator.add(existing_post)

        unique_posts = deduplicator.deduplicate(recent_posts)
        logger.info(f"After deduplication: {len(unique_posts)} posts")
        
        filtered_posts = self.filter.filter_posts(unique_posts)
        logger.info(f"After keyword filter: {len(filtered_posts)} posts")

        new_count = 0
        for post in filtered_posts:
            if not self.db.post_exists(post["url"]):
                self.db.save_post(
                    source_name=post["source_name"],
                    title=post["title"],
                    url=post["url"],
                    summary=post.get("summary", ""),
                    tags=post.get("tags", ""),
                    published_at=post.get("published_at", ""),
                    matched_keywords=post.get("matched_keywords", ""),
                    relevance_score=post.get("relevance_score", 0),
                )
                new_count += 1

        logger.info(f"Saved {new_count} new posts to database")
        return new_count

    async def send_notifications(self):
        unsent_posts = self.db.get_unsent_posts()
        if not unsent_posts:
            logger.info("No unsent posts to notify")
            return 0

        logger.info(f"Sending {len(unsent_posts)} notifications...")

        sent_count = 0
        for post in unsent_posts:
            try:
                was_sent = await self.notifier.send_post(post)
                if not was_sent:
                    logger.warning(
                        f"Notification not sent for post {post['id']}; leaving it unsent"
                    )
                    continue

                self.db.mark_as_sent(post["id"])
                sent_count += 1
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error sending notification for post {post['id']}: {e}")

        logger.info(f"Sent {sent_count} notifications")
        return sent_count

    async def run_cycle(self):
        await self.collect_and_filter()
        await self.send_notifications()

    async def run(self):
        logger.info("Starting Skill Community Bot...")
        self.running = True

        await self.notifier.wait_until_ready()
        logger.info("Discord bot is ready")

        await self.run_cycle()

        while self.running:
            next_time = get_next_scheduled_time()
            sleep_seconds = (next_time - datetime.now()).total_seconds()
            
            logger.info(f"Next collection at {next_time.strftime('%H:%M')} (sleeping {sleep_seconds/3600:.1f} hours)")
            await asyncio.sleep(sleep_seconds)

            if self.running:
                await self.run_cycle()

    async def stop(self):
        logger.info("Stopping bot...")
        self.running = False
        await self.notifier.close()


async def main():
    if not DISCORD_BOT_TOKEN or not DISCORD_CHANNEL_ID:
        logger.error("DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID must be set")
        return

    bot = SkillCommunityBot()

    notifier_task = asyncio.create_task(bot.notifier.start())
    bot_task = asyncio.create_task(bot.run())

    try:
        await asyncio.gather(notifier_task, bot_task)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
