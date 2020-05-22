# async def metrics(request):
#     errors = request.app["dm"].errors
#     msgs = [
#         "csgo_hermes_alive 1",
#         f"csgo_hermes_errors {errors}",
#     ]
#     return web.Response(text="\n".join(msgs))
#
#
# from aiohttp import web
# import os
#
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#
#     app = web.Application()
#
#     bot = commands.Bot(command_prefix="$")
#     cog = DiscordManager(bot)
#     bot.add_cog(cog)
#
#     app["dm"] = cog
#     app.add_routes([web.get("/metrics", metrics)])
#
#     runner = web.AppRunner(app)
#
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(runner.setup())
#
#     site = web.TCPSite(runner, 'localhost', 8080)
#
#     loop.create_task(bot.start(os.environ["DISCORD_TOKEN"]))
#     loop.create_task(site.start())
#
#     loop.run_forever()
