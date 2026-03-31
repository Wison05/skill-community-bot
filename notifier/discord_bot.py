import discord
from discord.ext import commands
from typing import Dict, Any
import asyncio


class DiscordNotifier:
    def __init__(self, bot_token: str, channel_id: int):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
        self.ready_event = asyncio.Event()

        @self.bot.event
        async def on_ready():
            self.ready_event.set()

    async def start(self):
        await self.bot.start(self.bot_token)

    async def wait_until_ready(self):
        await self.ready_event.wait()

    async def send_post(self, post: Dict[str, Any]):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return False

        embed = self._create_embed(post)
        await channel.send(embed=embed)
        return True

    def _create_embed(self, post: Dict[str, Any]) -> discord.Embed:
        source = post.get("source_name", "Unknown")
        title = post.get("title", "No title")
        url = post.get("url", "")
        summary = post.get("summary", "")
        tags = post.get("tags", "")
        keywords = post.get("matched_keywords", "")
        score = post.get("relevance_score", 0)

        embed = discord.Embed(
            title=title[:256],
            url=url,
            description=summary[:4096] if summary else None,
            color=discord.Color.blue(),
        )

        embed.set_author(name=f"[{source}]")

        if tags:
            embed.add_field(name="Tags", value=tags[:1024], inline=False)

        if keywords:
            embed.add_field(name="Matched Keywords", value=keywords[:1024], inline=True)

        embed.add_field(name="Score", value=f"{score:.1f}", inline=True)

        return embed

    async def close(self):
        await self.bot.close()
