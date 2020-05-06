import asyncio
from enum import Enum
import os
import socket
import sys
import traceback

from aiohttp import web
import a2s
import digitalocean
from discord.ext import commands, tasks
import jinja2


ADMIN = 666716587083956224
HERMES = 701189984132136990


def loop(time):
    def timer(f):
        async def looper(*args, **kwargs):
            while True:
                try:
                    await f(*args, **kwargs)
                except Exception as e:
                    traceback.print_exc(file=sys.stdout)
                    sys.exit(1)
                await asyncio.sleep(time)

        return looper

    return timer


class State(Enum):
    UNKNOWN = 0
    OFF = 1
    ON = 2
    STARTING = 3
    STOPPING = 4


class Server:
    def __init__(self, name, q):
        self.name = name
        self.q = q

        self.current = State.UNKNOWN
        self.desired = State.UNKNOWN
        self.droplet = None
        self.csgo = False
        self.csgo_info = None
        self.timeout_cur = 0
        self.timeout_max = 900

    async def update_csgo(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        csgo_conn = sock.connect_ex((f"{self.name}.rdkr.uk", 27015)) == 0
        if csgo_conn:
            self.csgo_info = a2s.info((f"{self.name}.rdkr.uk", 27015))
        return await self.update(csgo=csgo_conn)

    async def update_state(self):

        if self.current == State.UNKNOWN:
            if self.droplet and self.csgo:
                await self.update(current=State.ON)
            elif self.droplet and not self.csgo:
                await self.update(current=State.STARTING)
            else:
                await self.update(current=State.OFF)

        if self.current in [State.STARTING] and self.csgo:
            await self.update(current=State.ON)

        elif self.current in [State.ON, State.STOPPING] and not self.droplet:
            await self.update(current=State.OFF)

        elif self.current in [State.ON] and self.csgo:
            if self.csgo_info.player_count > 0:
                self.timeout_cur = 0
            elif self.timeout_cur > self.timeout_max:
                await self.update(desired=State.OFF)
            else:
                self.timeout_cur = self.timeout_cur + 1

        elif self.current in [State.ON] and not self.csgo:
            await self.update(current=State.STARTING)

        if self.desired == State.ON:
            if self.current in [State.OFF]:
                await self.create()

        if self.desired == State.OFF:
            await self.destroy()

    async def create(self):

        with open(f"{self.name}/cloud-config.yaml") as f:
            template = jinja2.Template(f.read())
            user_data = template.render(env=os.environ)

        digitalocean.Droplet(
            token=os.environ["DO_TOKEN"],
            name=f"csgo-{self.name}",
            region="lon1",
            image="62537048",
            size_slug="s-1vcpu-2gb",
            ssh_keys=[
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGs5SOHcst8xy0Te3LR3/0fGIIYaTc3yLnts1ZZQLuvn neel@Neels-MBP"
            ],
            backups=False,
            user_data=user_data,
        ).create()

        await self.update(current=State.STARTING)

    async def destroy(self):
        if self.droplet:
            try:
                self.droplet.destroy()
            except digitalocean.baseapi.NotFoundError:
                pass
            await self.update(current=State.STOPPING)

    async def update(self, **kwargs):
        for key, new in kwargs.items():
            old = self.__getattribute__(key)
            if old != new:
                self.__setattr__(key, new)
                change = f"Δ{key}:{old}->{new}"
                if not (key == "droplet" and old and new and old.id == new.id):
                    self.report(f"{change};")
                    await self.q.put((self.name, key, change))

    def get_status(self):
        return dict(
            csgo_current=self.current.value,
            csgo_desired=self.desired.value,
            csgo_version=int(self.csgo_info.version.replace(".", ""))
            if self.csgo
            else 0,
            csgo_player_count=self.csgo_info.player_count if self.csgo else 0,
            csgo_max_players=self.csgo_info.max_players if self.csgo else 0,
            csgo_ping=self.csgo_info.ping if self.csgo else 0,
            csgo_timeout_cur=self.timeout_cur,
            csgo_timeout_max=self.timeout_max,
            csgo_droplet=self.droplet.id if self.droplet else 0,
        )

    def report(self, action):
        print(f"{list(self.get_status().values())}; {action}")


class ServerManager:
    def __init__(self):

        self.q = asyncio.Queue()

        self.servers = {"pug": Server("pug", self.q), "dm": Server("dm", self.q)}

    async def start(self, app):
        asyncio.create_task(self.manager_droplet_loop())
        asyncio.create_task(self.manager_dns_loop())
        asyncio.create_task(self.servers_csgo_loop())
        asyncio.create_task(self.servers_status_loop())

    @loop(10)
    async def manager_droplet_loop(self):

        droplets_list = digitalocean.Manager(
            token=os.environ["DO_TOKEN"]
        ).get_all_droplets()

        csgo_list = [d for d in droplets_list if d.name.startswith("csgo")]

        if len(csgo_list) > 2:
            print(f"emergency stopping {len(droplets_list)} droplets")
            for d in csgo_list:
                d.destroy()

        droplets = {d.name.replace("csgo-", ""): d for d in csgo_list}

        for server in self.servers.values():
            droplet = droplets.get(server.name, None)
            await server.update(droplet=droplet)

    @loop(10)
    async def manager_dns_loop(self):
        for name, server in self.servers.items():

            if not server.droplet or not server.droplet.ip_address:
                continue

            domain = digitalocean.Domain(
                token=os.environ["DO_TOKEN"], name=f"{name}.rdkr.uk"
            )
            correct = False
            for r in domain.get_records():
                if r.type == "A":
                    if r.data == server.droplet.ip_address:
                        correct = True
                    else:
                        print(f"dns {name} destroy: {r}")
                        r.destroy()

            if not correct:
                record = dict(
                    type="A", name="@", ttl=60, data=server.droplet.ip_address
                )
                print(f"dns {name} create: {record}")
                domain.create_new_domain_record(**record)

    @loop(10)
    async def servers_csgo_loop(self):
        for server in self.servers.values():
            await server.update_csgo()

    @loop(10)
    async def servers_status_loop(self):
        for server in self.servers.values():
            await server.update_state()


class DiscordManager(commands.Cog):
    def __init__(self, bot, gameserver_manager, token):
        self.bot = bot
        self.channel = None
        self.gameserver_manager = gameserver_manager
        self.token = token

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
                if key == "droplet":
                    continue
                await self.message(f"update for **{name}.rdkr.uk**\n`{change}`")
            except Exception as e:
                print(e)

    @commands.Cog.listener()
    async def on_message(self, message):
        channel = ADMIN if message.channel.id == ADMIN else HERMES
        self.channel = self.bot.get_channel(channel)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        await ctx.send(f"```Command error: {exception}```")

    @commands.command()
    async def status(self, ctx):
        for name, server in self.gameserver_manager.servers.items():
            status = server.get_status()
            pretty_status = ""
            for key, value in status.items():
                key = key.replace('csgo_', '')
                if key in ['current', 'desired']:
                    value = State(value)
                if value == 0:
                    continue
                line = f"{key.ljust(14)} {value}\n"
                pretty_status = pretty_status + line
            await ctx.send(f"server status for **{name}.rdkr.uk**\n```{pretty_status}```")

    @commands.command()
    async def start(self, ctx, server_name):
        await self.gameserver_manager.servers[server_name].update(desired=State.ON)

    @commands.command()
    async def stop(self, ctx, server_name):
        await self.gameserver_manager.servers[server_name].update(desired=State.OFF)


async def metrics(request):
    msgs = ['csgo_hermes_alive 1']
    for server in request.app["manager"].servers.values():
        status = server.get_status()
        for k, v in status.items():
            msgs.append(f'{k}{{name="{server.name}"}} {v}')
    return web.Response(text="\n".join(msgs))


async def start(request):
    await request.app["manager"].servers[request.match_info.get("name")].update(
        desired=State.ON
    )
    return web.Response()


async def stop(request):
    await request.app["manager"].servers[request.match_info.get("name")].update(
        desired=State.OFF
    )
    return web.Response()


if __name__ == "__main__":

    app = web.Application()

    gameserver_manager = ServerManager()
    discord_bot = commands.Bot(command_prefix="!")
    discord_manager = DiscordManager(
        discord_bot, gameserver_manager, os.environ["DISCORD_TOKEN"]
    )
    discord_bot.add_cog(discord_manager)

    app.on_startup.append(gameserver_manager.start)
    app.on_startup.append(discord_manager.start_with_token)

    app.add_routes(
        [
            web.get("/metrics", metrics),
            web.post("/start/{name}", start),
            web.post("/stop/{name}", stop),
        ]
    )
    web.run_app(app)
