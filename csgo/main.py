import os

import digitalocean
import discord
import jinja2


client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!help'):
        await message.channel.send('_!startpug_ or _!stoppug_')

    if message.content.startswith('!stoppug'):

        await message.channel.send('[pug.rdkr.uk] checking status...')

        try:

            manager = digitalocean.Manager(token=os.environ['DO_TOKEN'])
            my_droplets = manager.get_all_droplets()

            for droplet in my_droplets:
                if droplet.name == 'pug':
                    await message.channel.send(f'[pug.rdkr.uk] is {droplet.status}')
                    await message.channel.send('[pug.rdkr.uk] destroying...')
                    droplet.destroy()
                    for action in droplet.get_actions():
                        action.load()
                    await message.channel.send(f'[pug.rdkr.uk] is {action.status}')
                    return
            
            await message.channel.send(f'[pug.rdkr.uk] not found')

        except Exception as e:
            await message.channel.send(e)

    if message.content.startswith('!startpug'):

        await message.channel.send('[pug.rdkr.uk] checking status...')

        try:

            manager = digitalocean.Manager(token=os.environ['DO_TOKEN'])
            my_droplets = manager.get_all_droplets()

            for droplet in my_droplets:
                if droplet.name == 'pug':
                    await message.channel.send(f'[pug.rdkr.uk] is {droplet.status}')
                    return
            
            await message.channel.send(f'[pug.rdkr.uk] not found...')
            
            with open('pug/cloud-config.yaml') as f:
                template = jinja2.Template(f.read())
                user_data = template.render(env=os.environ)

            droplet = digitalocean.Droplet(
                token=os.environ['DO_TOKEN'],
                name='pug',
                region='lon1',
                image='62093009',
                size_slug='s-1vcpu-2gb',
                ssh_keys=['ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGs5SOHcst8xy0Te3LR3/0fGIIYaTc3yLnts1ZZQLuvn neel@Neels-MBP'],
                backups=False,
                user_data=user_data
            )
            
            await message.channel.send('[pug.rdkr.uk] creating...')
            droplet.create()

            actions = droplet.get_actions()
            for action in actions:
                action.load()
            await message.channel.send(f'[pug.rdkr.uk] is {action.status}')

        except Exception as e:
            await message.channel.send(e)


client.run(os.environ['DISCORD_TOKEN'])
