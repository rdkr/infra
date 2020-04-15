import asyncio
import os
import socket
import time

import digitalocean
import discord
import jinja2

from discord.ext import commands


bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))
    activity = discord.Activity(name="CSGO servers", type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!help"):
        return await message.channel.send(
            ":yellow_circle:  usage: _!<start|stop> <pug|dm>_"
        )

    if message.content.startswith("!start") or message.content.startswith("!stop"):
        cmd = message.content.split(" ")
        if len(cmd) != 2 or cmd[1] not in ["pug", "dm"]:
            print(f"start: rejecting {message}")
            return await message.channel.send(
                ":yellow_circle:  usage: _!<start|stop> <pug|dm>_"
            )

        if message.content.startswith("!start"):
            return await servers[cmd[1]].start(message)

        if message.content.startswith("!stop"):
            return await servers[cmd[1]].stop(message)

from enum import Enum
class State(Enum):
    OFF = 0
    CREATING = 1
    ON = 2
    STOPPING = 3


class Server:
    def __init__(self, name):
        self.name = name
        self.current = None
        self.desired = None
        self.droplet = None
        self.csgo = None

    async def update_csgo(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        self.csgo = sock.connect_ex((f"{self.name}.rdkr.uk", 27015)) == 0

    async def update_state(self):
        try:

            print(self.name, self.desired, self.current, self.droplet, self.csgo)
            await self.update_csgo()

            if self.csgo:
                self.current = State.ON
            if not self.droplet: 
                self.current = State.OFF

            if self.desired == State.ON:
                print('oyoyo')
                if self.current == State.STOPPING:
                    return 0 
                elif self.current == State.OFF:
                    await self.create()
                elif self.current == State.CREATING:
                    await self.set_dns()

        except:
            raise
        # elif self.desired == State.OFF:
        #     if self.current == State.CREATING:
        #         return 0 
        #     elif self.current == State.STOPPING:
        #         return assure_stop()
        #     elif self.current == State.ON:
        #         self.current == State.STOPPING
        #         return self.stop()



    async def start(self, message):
        print(f"start: got {message.author.name}")
        self.desired = State.ON
        print(self.desired)


    async def create(self):
        print(f"start: create")

        try:

            with open(f"{self.name}/cloud-config.yaml") as f:
                template = jinja2.Template(f.read())
                user_data = template.render(env=os.environ)

            digitalocean.Droplet(
                token=os.environ["DO_TOKEN"],
                name=self.name,
                region="lon1",
                image="62093009",
                size_slug="s-1vcpu-2gb",
                ssh_keys=[
                    "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGs5SOHcst8xy0Te3LR3/0fGIIYaTc3yLnts1ZZQLuvn neel@Neels-MBP"
                ],
                backups=False,
                user_data=user_data,
            ).create()

            self.current == State.CREATING

        except Exception as e:
            raise print(f'error {e}')

        # server = None
        # creating = False
        # manager = digitalocean.Manager(token=os.environ["DO_TOKEN"])

        # timeout = 120
        # while timeout != 0:

        #     if self.droplet:
        #         return await message.channel.send(
        #             f":green_circle:  [{self.name}.rdkr.uk] [instance] exists"
        #         )


        #     if not server and not creating:
        #         await message.channel.send(
        #             f":white_circle:  [{self.name}.rdkr.uk] [instance] not found - creating..."
        #         )


    async def set_dns(self):

        print(f"start: set_dns")

        if not self.droplet:
            print(f'set_dns: no droplet')
            return
        if not self.droplet.ip:
            print(f'set_dns: no ip')
            return

        domain = digitalocean.Domain(
            token=os.environ["DO_TOKEN"], name=f"{self.name}.rdkr.uk"
        )

        records = domain.get_records()
        for r in records:
            if r.type == "A":
                r.destroy()

        domain.create_new_domain_record(type="A", name="@", ttl=60, data=ip)

        # await message.channel.send(
        #     f":green_circle:  [{self.name}.rdkr.uk] [dns] set to {ip}"
        # )

    # async def wait_for_csgo(self, message):

    #     print(f"start: wait_for_csgo")

    #     timeout = 120
    #     while timeout != 0:

    #         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         sock.settimeout(1)
    #         result = sock.connect_ex((f"{self.name}.rdkr.uk", 27015))

    #         if result == 0:
    #             await message.channel.send(
    #                 f":green_circle:  [{self.name}.rdkr.uk] [csgo] appears to be alive"
    #             )
    #             return

    #         if timeout % 24 == 0:
    #             await message.channel.send(
    #                 f":white_circle:  [{self.name}.rdkr.uk] [csgo] waiting for server..."
    #             )

    #         timeout = timeout - 1
    #         await asyncio.sleep(5)

    #     else:
    #         raise Exception("is not alive before timeout")

    async def stop(self, message):

        print(f"stop: got {message.author.name}")

        try:

            timeout = 120
            while timeout != 0:

                manager = digitalocean.Manager(token=os.environ["DO_TOKEN"])
                my_droplets = manager.get_all_droplets()

                for droplet in my_droplets:
                    if droplet.name == self.name:
                        droplet.destroy()
                    else:
                        return await message.channel.send(
                            f":green_circle:  [{self.name}.rdkr.uk] not found"
                        )

                if timeout % 24 == 0:
                    await message.channel.send(
                        f":white_circle:  [{self.name}.rdkr.uk] [instance] waiting for stop..."
                    )

                timeout = timeout - 1
                await asyncio.sleep(5)

        except Exception as e:
            print(f"stop: error: {e}")
            await message.channel.send(
                f":red_circle:  [{self.name}.rdkr.uk] [csgo] error: {e}"
            )





from discord.ext import tasks, commands

class MyCog(commands.Cog):
    def __init__(self):
        self.index = 0
        self.servers = {"pug": Server("pug"), "dm": Server("dm")}
        self.server_loop.start()
        self.status_loop.start()

    def cog_unload(self):
        self.server_loop.cancel()
        self.status_loop.start()

    @tasks.loop(seconds=10.0)
    async def server_loop(self):
        manager = digitalocean.Manager(token=os.environ["DO_TOKEN"])
        droplets = {d.name: d for d in manager.get_all_droplets()}
        for server in self.servers.values():
            server.droplet = droplets[server.name] if server.name in droplets.keys() else None

    @tasks.loop(seconds=5.0)
    async def status_loop(self):
        for server in self.servers.values():
            try:
                await server.update_state()
            except:
                raise


servers = {"pug": Server("pug"), "dm": Server("dm")}
bot.add_cog(MyCog())
bot.run(os.environ["DISCORD_TOKEN"])