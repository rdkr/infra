import logging
import os
import socket
from enum import Enum

import a2s
import digitalocean
import jinja2


class State(Enum):
    UNKNOWN = 0
    OFF = 1
    STARTING = 2
    STOPPING = 3
    ON = 4


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
        self.timeout_max = 180

    async def update_csgo(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            csgo_conn = sock.connect_ex((f"{self.name}.rdkr.uk", 27015)) == 0
        except socket.timeout:
            csgo_conn = False
        if csgo_conn:
            self.csgo_info = a2s.info((f"{self.name}.rdkr.uk", 27015))
        return await self.update(csgo=csgo_conn)

    async def update_state(self):

        if self.current == State.UNKNOWN:
            if self.csgo:
                await self.update(current=State.ON)
            else:
                await self.update(current=State.OFF)

        elif self.current == State.STARTING:
            if self.csgo:
                await self.update(current=State.ON)

        elif self.current == State.STOPPING:
            if not self.droplet:
                await self.update(current=State.OFF)

        elif self.current == State.OFF:
            if self.desired == State.ON:
                await self.update(current=State.STARTING)
                await self.create()
            elif self.csgo:
                await self.update(current=State.ON)

        elif self.current == State.ON:
            if not self.droplet:
                await self.update(current=State.OFF)

            elif self.desired == State.OFF:
                await self.update(current=State.STOPPING)
                await self.destroy()

            else:
                if self.csgo_info.player_count > 0:
                    self.timeout_cur = 0
                elif self.timeout_cur == self.timeout_max:
                    self.timeout_cur = 0
                    await self.update(desired=State.OFF)
                else:
                    self.timeout_cur = self.timeout_cur + 1

    async def create(self):

        with open(f"cloud-config/{self.name}.yaml") as f:
            template = jinja2.Template(f.read())
            user_data = template.render(env=os.environ)

        digitalocean.Droplet(
            token=os.environ["DO_TOKEN"],
            name=f"csgo-{self.name}",
            region="lon1",
            image="63267584",
            size_slug="s-1vcpu-2gb",
            ssh_keys=[
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGs5SOHcst8xy0Te3LR3/0fGIIYaTc3yLnts1ZZQLuvn neel@Neels-MBP"
            ],
            backups=False,
            user_data=user_data,
        ).create()

    async def destroy(self):
        try:
            self.droplet.destroy()
        except digitalocean.baseapi.NotFoundError:
            pass

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
        csgo = int(self.csgo_info.version.replace(".", "")) if self.csgo else 0
        return dict(
            csgo_current=self.current.value,
            csgo_desired=self.desired.value,
            csgo_version=csgo,
            csgo_player_count=self.csgo_info.player_count if self.csgo else 0,
            csgo_max_players=self.csgo_info.max_players if self.csgo else 0,
            csgo_ping=self.csgo_info.ping if self.csgo else 0,
            csgo_timeout_cur=self.timeout_cur,
            csgo_timeout_max=self.timeout_max,
            csgo_droplet=self.droplet.id if self.droplet else 0,
        )

    def report(self, action):
        logging.info(f"{list(self.get_status().values())}; {action}")
