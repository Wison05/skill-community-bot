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
from collectors import DevCommunityCollector, HackerNewsCollector, GitHubTrendingCollector, RedditCollector, HadaNewsCollector
from filters import KeywordFilter, Deduplicator, TimeFilter
from notifier import DiscordNotifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_next_scheduled_time():
    now = datetime.now()
    interval_minutes = max(1, int(COLLECTION_INTERVAL_HOURS * 60))
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elapsed_minutes = int((now - day_start).total_seconds() // 60)
    next_slot_minutes = ((elapsed_minutes // interval_minutes) + 1) * interval_minutes
    target = day_start + timedelta(minutes=next_slot_minutes)
    target = target.replace(second=0, microsecond=0)
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

    def _mark_notification_failed(self, post_id: int, error_message: str):
        try:
            was_marked_failed = self.db.mark_as_failed(post_id, error_message)
            if not was_marked_failed:
                logger.error(
                    f"Failed to move post {post_id} into failed notification state"
                )
        except Exception as db_error:
            logger.error(
                f"Could not persist failed notification state for post {post_id}: {db_error}"
            )

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
            was_saved = self.db.save_post(
                source_name=post["source_name"],
                title=post["title"],
                url=post["url"],
                summary=post.get("summary", ""),
                tags=post.get("tags", ""),
                published_at=post.get("published_at", ""),
                matched_keywords=post.get("matched_keywords", ""),
                relevance_score=post.get("relevance_score", 0),
            )
            if was_saved:
                new_count += 1
            else:
                logger.info(
                    f"Post was not saved for source {post['source_name']}: {post['url']}"
                )

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
            post_id = post["id"]

            try:
                was_claimed = self.db.mark_as_sending(post_id)
                if not was_claimed:
                    logger.warning(f"Notification already claimed for post {post_id}")
                    continue

                discord_message_id = await self.notifier.send_post(post)
                if not discord_message_id:
                    self._mark_notification_failed(
                        post_id,
                        "Notifier did not return a Discord message id",
                    )
                    logger.warning(
                        f"Notification not sent for post {post_id}; moving it to failed state"
                    )
                    continue

            except Exception as e:
                self._mark_notification_failed(post_id, str(e))
                logger.error(f"Error sending notification for post {post_id}: {e}")
                continue

            try:
                was_marked_sent = self.db.mark_as_sent(post_id, discord_message_id)
                if not was_marked_sent:
                    logger.error(
                        f"Sent Discord message {discord_message_id} for post {post_id} but could not finalize DB state; leaving it in sending state"
                    )
                    continue

                sent_count += 1
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(
                    f"Sent Discord message {discord_message_id} for post {post_id} but failed to persist sent state: {e}"
                )

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
