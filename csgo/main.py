import asyncio
import a2s
import queue
from enum import Enum
import os
import socket
import time

import digitalocean
import discord
from discord.ext import tasks, commands
import jinja2

ADMIN = 666716587083956224
HERMES = 701189984132136990


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
            elif self.inactive > 60 * 15:
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
            image="62093009",
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
                    await self.q.put((self.name, key))

    def get_status(self):
        if self.csgo:
            csgo = f"v{self.csgo_info.version}, {self.csgo_info.player_count}/{self.csgo_info.max_players}, {round(self.csgo_info.ping*1000)}ms, {self.inactive}"
        if self.droplet:
            droplet = self.droplet.id
        return dict(
            name=self.name,
            current=f"{self.current}",
            desired=f"{self.desired}",
            csgo=csgo if self.csgo else None,
            droplet=droplet if self.droplet else None,
        )

    def report(self, action):
        print(f"{list(self.get_status().values())}; {action}")


class ServerManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.q = asyncio.Queue()

        self.servers = {"pug": Server("pug", self.q), "dm": Server("dm", self.q)}
        self.channel = self.bot.get_channel(ADMIN)

        self.manager_status_loop.start()
        self.manager_droplet_loop.start()
        self.manager_dns_loop.start()
        self.servers_csgo_loop.start()
        self.servers_status_loop.start()

    @tasks.loop(loop=None)
    async def manager_status_loop(self):
        while True:
            msg = await self.q.get()
            content = self.servers[msg[0]].get_status()[msg[1]]
            if content == "None" or msg[1] == "droplet":
                return
            await self.channel.send(
                f"update for **{msg[0]}.rdkr.uk**\n`{msg[1]}: {content}`"
            )

    @tasks.loop(seconds=10.0, reconnect=False)
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

    @tasks.loop(seconds=10.0)
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

    @tasks.loop(seconds=10.0)
    async def servers_csgo_loop(self):
        for server in self.servers.values():
            await server.update_csgo()

    @tasks.loop(seconds=1, reconnect=False)
    async def servers_status_loop(self):
        for server in self.servers.values():
            await server.update_state()

    @commands.Cog.listener()
    async def on_message(self, message):
        channel = ADMIN if message.channel == ADMIN else HERMES
        self.channel = self.bot.get_channel(channel)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        await ctx.send(f"```Command error: {exception}```")

    @commands.command()
    async def status(self, ctx):
        for server in self.servers.values():
            status = server.get_status()
            status_items = "\n".join(
                [f"{k.ljust(7, ' ')}: {v}" for k, v in status.items() if k != "name"]
            )
            msg = f'server status for **{status["name"]}.rdkr.uk**```{status_items}```'
            await ctx.send(msg)

    @commands.command()
    async def start(self, ctx, server_name):
        await self.servers[server_name].update(desired=State.ON)

    @commands.command()
    async def stop(self, ctx, server_name):
        await self.servers[server_name].update(desired=State.OFF)


bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))
    bot.add_cog(ServerManager(bot))


bot.run(os.environ["DISCORD_TOKEN"])
