import os

from jinja2 import Template
import digitalocean


with open('cloud-config.yaml') as f:
    template = Template(f.read())
    print(template.render(env=os.environ))

manager = digitalocean.Manager(token=os.environ['DO_TOKEN'])
my_droplets = manager.get_all_droplets()
print(my_droplets)

for droplet in my_droplets:
    if droplet.name == 'packer-5e94f01a-9481-c637-9151-2d20f0fd93ec':
        print(droplet.name)
