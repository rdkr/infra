import logging
import os

from aiohttp import web

from hermes.discord_manager import DiscordManager
from hermes.server_manager import ServerManager
from hermes.server import State

logging.basicConfig(level=logging.INFO)


async def metrics(request):
    errors = request.app['server_manager'].errors + request.app['discord_manager'].errors
    msgs = [
        "csgo_hermes_alive 1",
        f"csgo_hermes_errors {errors}",
    ]
    for server in request.app["server_manager"].servers.values():
        status = server.get_status()
        for k, v in status.items():
            msgs.append(f'{k}{{name="{server.name}"}} {v}')
    return web.Response(text="\n".join(msgs))


async def start(request):
    await request.app["server_manager"].servers[request.match_info.get("name")].update(
        desired=State.ON
    )
    return web.Response()


async def stop(request):
    await request.app["server_manager"].servers[request.match_info.get("name")].update(
        desired=State.OFF
    )
    return web.Response()


if __name__ == "__main__":

    app = web.Application()

    app["server_manager"] = ServerManager()
    app["discord_manager"] = DiscordManager(
        app["server_manager"], os.environ["DISCORD_TOKEN"]
    )

    app.on_startup.append(app["server_manager"].start)
    app.on_startup.append(app["discord_manager"].start_with_token)

    app.add_routes(
        [
            web.get("/metrics", metrics),
            web.post("/start/{name}", start),
            web.post("/stop/{name}", stop),
        ]
    )
    web.run_app(app, access_log=None)
