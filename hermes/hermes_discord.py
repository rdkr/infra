import os

import aiohttp
from discord.ext import commands

ADMIN = 666716587083956224
HERMES = 701189984132136990

class ServerManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = self.bot.get_channel(ADMIN)
        self.session = aiohttp.ClientSession()

    @commands.Cog.listener()
    async def on_message(self, message):
        channel = ADMIN if message.channel.id == ADMIN else HERMES
        self.channel = self.bot.get_channel(channel)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        await ctx.send(f"```Command error: {exception}```")

    # @commands.command()
    # async def status(self, ctx):
    #     for server in self.servers.values():
    #         status = server.get_status()
    #         status_items = "\n".join(
    #             [f"{k.ljust(7, ' ')}: {v}" for k, v in status.items() if k != "name"]
    #         )
    #         msg = f'server status for **{status["name"]}.rdkr.uk**```{status_items}```'
    #         await ctx.send(msg)

    @commands.command()
    async def start(self, ctx, server_name):
        print(f'starting {server_name}')
        self.session.post(f'http://hermes/start/{server_name}')

    @commands.command()
    async def stop(self, ctx, server_name):
        print(f'stopping {server_name}')
        self.session.post(f'http://hermes/stop/{server_name}')


bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))
    bot.add_cog(ServerManager(bot))

bot.run(os.environ["DISCORD_TOKEN"])
