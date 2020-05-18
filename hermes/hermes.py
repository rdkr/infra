import logging
import os

from aiohttp import web

from hermes.discord_manager import DiscordManager
from hermes.server_manager import ServerManager


async def metrics(request):
    errors = request.app["sm"].errors + request.app["dm"].errors
    msgs = [
        "csgo_hermes_alive 1",
        f"csgo_hermes_errors {errors}",
    ]
    for server in request.app["sm"].servers.values():
        status = server.get_status()
        for k, v in status.items():
            msgs.append(f'{k}{{name="{server.name}"}} {v}')
    return web.Response(text="\n".join(msgs))


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    app = web.Application()

    app["sm"] = ServerManager()
    app["dm"] = DiscordManager(app["sm"], os.environ["DISCORD_TOKEN"])

    app.on_startup.append(app["sm"].start)
    app.on_startup.append(app["dm"].start_with_token)

    app.add_routes([web.get("/metrics", metrics)])
    web.run_app(app, access_log=None)
