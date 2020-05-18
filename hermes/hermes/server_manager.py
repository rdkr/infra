import asyncio
import logging
import os
import sys
import traceback

import digitalocean

from hermes.server import Server


def loop(time):
    def decorator(f):
        async def wrapper(self, *args, **kwargs):
            while True:
                try:
                    await f(self, *args, **kwargs)
                except Exception as e:
                    traceback.print_exc(file=sys.stdout)
                    self.errors = self.errors + 1
                await asyncio.sleep(time)

        return wrapper

    return decorator


class ServerManager:
    def __init__(self):
        self.q = asyncio.Queue()
        self.errors = 0
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
            logging.warning(f"emergency stopping {len(droplets_list)} droplets")
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
                        logging.info(f"dns {name} destroy: {r}")
                        r.destroy()

            if not correct:
                record = dict(
                    type="A", name="@", ttl=60, data=server.droplet.ip_address
                )
                logging.info(f"dns {name} create: {record}")
                domain.create_new_domain_record(**record)

    @loop(10)
    async def servers_csgo_loop(self):
        for server in self.servers.values():
            await server.update_csgo()

    @loop(10)
    async def servers_status_loop(self):
        for server in self.servers.values():
            await server.update_state()
