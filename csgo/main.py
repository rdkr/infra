import enum
import os
import socket
import time

import digitalocean
import discord
import jinja2

client = discord.Client()


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    activity = discord.Activity(name="CSGO servers", type=discord.ActivityType.watching)
    await client.change_presence(activity=activity)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!help"):
        await message.channel.send("_!start_ or _!stop_")

    if message.content.startswith("!start"):
        await servers["pug"].start(message)

    if message.content.startswith("!stop"):
        await servers["pug"].stop(message)


class Status(enum.Enum):
    STARTING = 1
    ON = 2
    OFF = 3
    STOPPING = 4


class Server:
    def __init__(self, name):
        self.name = name
        self.state = None

    async def start(self, message):

        print(f"start: got {message}")

        # cmd = message.content.split(" ")
        # if len(cmd) != 2 or cmd[1] not in ["pug", "dm"]:
        #     print(f"start: rejecting {message}")
        #     return await message.channel.send("_!start pug_")

        try:

            server = await self.create(message)
            ip = await self.get_ip(server, message)
            await self.set_dns(ip, message)
            await self.wait_for_csgo(message)

            print("done")

        except Exception as e:
            await message.channel.send(
                f":red_circle: [{self.name}.rdkr.uk] [csgo] error: {e}"
            )

    async def create(self, message):

        print(f"start: create")

        with open(f"{self.name}/cloud-config.yaml") as f:
            template = jinja2.Template(f.read())
            user_data = template.render(env=os.environ)

        server = None
        creating = False
        manager = digitalocean.Manager(token=os.environ["DO_TOKEN"])

        timeout = 120
        while timeout != 0:

            for droplet in manager.get_all_droplets():
                if droplet.name == self.name:
                    await message.channel.send(
                        f":green_circle: [{self.name}.rdkr.uk] [instance] exists"
                    )
                    return droplet

            if not server and not creating:
                await message.channel.send(
                    ":white_circle: [{self.name}.rdkr.uk] [instance] not found - creating..."
                )

                creating = True

                droplet = digitalocean.Droplet(
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
                )
                droplet.create()

            if timeout % 24 == 0:
                await message.channel.send(
                    ":white_circle: [{self.name}.rdkr.uk] [instance] waiting for start..."
                )

            timeout = timeout - 1
            time.sleep(5)

        else:
            raise Exception("instance not found before timeout")

    async def get_ip(self, droplet, message):

        print(f"start: get_ip")

        timeout = 120
        while timeout != 0:

            actions = droplet.get_actions()
            for action in actions:
                action.load()

            if droplet.ip_address != None:
                return droplet.ip_address

            if timeout % 24 == 0:
                await message.channel.send(
                    f":white_circle: [{self.name}.rdkr.uk] [dns] waiting for ip..."
                )

            timeout = timeout - 1
            time.sleep(5)

        else:
            raise Exception("ip not found before timeout")

    async def set_dns(self, ip, message):

        print(f"start: set_dns")

        domain = digitalocean.Domain(
            token=os.environ["DO_TOKEN"], name=f"{self.name}.rdkr.uk"
        )

        records = domain.get_records()
        for r in records:
            if r.type == "A":
                r.destroy()

        domain.create_new_domain_record(type="A", name="@", ttl=60, data=ip)

        await message.channel.send(
            f":green_circle: [{self.name}.rdkr.uk] [dns] set to {ip}"
        )

    async def wait_for_csgo(self, message):

        print(f"start: wait_for_csgo")

        timeout = 120
        while timeout != 0:

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((f"{self.name}.rdkr.uk", 27015))

            if result == 0:
                await message.channel.send(
                    f":green_circle: [{self.name}.rdkr.uk] [csgo] appears to be alive"
                )
                return

            if timeout % 24 == 0:
                await message.channel.send(
                    f":white_circle: [{self.name}.rdkr.uk] [csgo] waiting for server..."
                )

            timeout = timeout - 1
            time.sleep(5)

        else:
            raise Exception("is not alive before timeout")

    async def stop(self, message):

        print(f"stop: got {message}")

        try:

            manager = digitalocean.Manager(token=os.environ["DO_TOKEN"])
            my_droplets = manager.get_all_droplets()

            for droplet in my_droplets:
                if droplet.name == self.name:
                    await message.channel.send(
                        f":white_circle: [{self.name}.rdkr.uk] destroying..."
                    )
                    droplet.destroy()
                    return  # todo check this worked

            await message.channel.send(
                f":green_circle: [{self.name}.rdkr.uk] not found"
            )

        except Exception as e:
            await message.channel.send(
                f":red_circle: [{self.name}.rdkr.uk] [csgo] error: {e}"
            )


servers = {"pug": Server("pug")}
client.run(os.environ["DISCORD_TOKEN"])
