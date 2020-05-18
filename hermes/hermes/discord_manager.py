import asyncio
import logging
import sys
import traceback

from discord.ext import commands, tasks

from hermes.server import State

ADMIN = 666716587083956224
HERMES = 701189984132136990


class DiscordManager(commands.Cog):
    def __init__(self, gameserver_manager, token):
        self.channel = None
        self.gameserver_manager = gameserver_manager
        self.token = token

        self.bot = commands.Bot(command_prefix="!")
        self.bot.add_cog(self)
        self.errors = 0

    async def message(self, message):
        if not self.channel:
            if not self.bot.is_ready():
                return
            self.channel = self.bot.get_channel(ADMIN)
        await self.channel.send(message)

    async def start_with_token(self, app):
        self.manager_status_loop.start()
        asyncio.create_task(self.bot.start(self.token))

    @tasks.loop(loop=None)
    async def manager_status_loop(self):
        while True:
            try:
                name, key, change = await self.gameserver_manager.q.get()
                if key in ["droplet", "csgo"]:
                    continue
                await self.message(f"update for **{name}.rdkr.uk**\n`{change}`")
            except Exception as e:
                logging.error(e)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith("!"):
            channel = ADMIN if message.channel.id == ADMIN else HERMES
            self.channel = self.bot.get_channel(channel)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        await ctx.send(f"```Command error: {exception}```")

    @commands.Cog.listener()
    async def on_error(self, ctx, exception):
        traceback.print_exc(file=sys.stdout)
        self.errors = self.errors + 1

    @commands.command()
    async def status(self, ctx):
        for name, server in self.gameserver_manager.servers.items():
            status = server.get_status()
            pretty_status = []
            pretty_status.append(f"current {State(status['csgo_current'])}")
            pretty_status.append(f"desired {State(status['csgo_desired'])}")
            if status["csgo_ping"] != 0:
                pretty_status.append(f"version {status['csgo_version']}")
                pretty_status.append(
                    f"players {status['csgo_player_count']}/{status['csgo_max_players']}"
                )
                pretty_status.append(
                    f"timeout {status['csgo_timeout_cur']}/{status['csgo_timeout_max']}"
                )
            msg = "\n".join(pretty_status)
            await ctx.send(f"server status for **{name}.rdkr.uk**\n```{msg}```")

    @commands.command()
    async def start(self, ctx, server_name):
        await self.gameserver_manager.servers[server_name].update(desired=State.ON)

    @commands.command()
    async def stop(self, ctx, server_name):
        await self.gameserver_manager.servers[server_name].update(desired=State.OFF)
