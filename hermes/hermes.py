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
        self.inactive = 0
        self.max_inactive = 720

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
                self.inactive = 0
            elif self.inactive > self.max_inactive:
                await self.update(desired=State.OFF)
            else:
                self.inactive = self.inactive + 1

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
            current=self.current.value,
            desired=self.desired.value,
            csgo_version=int(self.csgo_info.version.replace(".", ""))
            if self.csgo
            else -1,
            csgo_player_count=self.csgo_info.player_count if self.csgo else -1,
            csgo_max_players=self.csgo_info.max_players if self.csgo else -1,
            csgo_ping=self.csgo_info.ping if self.csgo else -1,
            csgo_inactive=self.inactive,
            csgo_max_inactive=self.max_inactive,
            droplet=self.droplet.id if self.droplet else -1,
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
    def __init__(self, bot, app, token):
        self.bot = bot
        self.app = app
        self.token = token

    async def start_with_token(self, app):
        self.manager_status_loop.start()
        asyncio.create_task(self.bot.start(self.token))

    @tasks.loop(loop=None)
    async def manager_status_loop(self):
        while True:
            name, key, change = await self.app["manager"].q.get()

            print(name, key, change)  #
            # for i in self.bot.get_all_channels():
            #     print("h", i)
            channel = self.bot.get_channel(ADMIN)
            channel = self.bot.guilds
            print(channel)
            if not channel:
                continue
            # if key == "droplet":
            #     continue
            # await self.channel.send('fd'
            #     f"update for **{name}.rdkr.uk**\n`{key}: {change}`"
            # )

    @commands.Cog.listener()
    async def on_message(self, message):
        channel = ADMIN if message.channel.id == ADMIN else HERMES
        self.channel = self.bot.get_channel(channel)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        await ctx.send(f"```Command error: {exception}```")

    @commands.command()
    async def status(self, ctx):
        for name, server in self.app["manager"].servers.items():
            status = server.get_status()
            await ctx.send(f"server status for **{name}.rdkr.uk**```{status}```")

    @commands.command()
    async def start(self, ctx, server_name):
        await self.app["manager"].servers[server_name].update(desired=State.ON)

    @commands.command()
    async def stop(self, ctx, server_name):
        await self.app["manager"].servers[server_name].update(desired=State.OFF)


async def metrics(request):
    msgs = []
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

    app["manager"] = ServerManager()
    app["dc_bot"] = commands.Bot(command_prefix="!")
    app["dc_manager"] = DiscordManager(app["dc_bot"], app, os.environ["DISCORD_TOKEN"])
    app["dc_bot"].add_cog(app["dc_manager"])
    app.on_startup.append(app["manager"].start)
    app.on_startup.append(app["dc_manager"].start_with_token)

    app.add_routes(
        [
            web.get("/metrics", metrics),
            web.post("/start/{name}", start),
            web.post("/stop/{name}", stop),
        ]
    )
    web.run_app(app)