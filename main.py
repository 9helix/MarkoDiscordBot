import asyncio
import json
import os
import random
import sys
from datetime import datetime, timedelta
import configparser

import discord
import requests
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands, tasks

# from keep_alive import keep_alive

from anime import *

bot = commands.Bot(command_prefix='-', intents=discord.Intents.all())

config = configparser.ConfigParser()
config.read('secret.ini')
admin = config["DEFAULT"].getint('admin_id')
my_channel = config["DEFAULT"].getint('my_channel')
token = config["DEFAULT"]['token']

f = open('database/devs.txt', 'a+')
f.seek(0)
devs = [user[:-1] for user in f.readlines()]
devs.append(admin)
f.close()

space = '<:space:988547133902819378>'
ojou = '<:ojou:990313694204395540>'

dms = ['bok', 'yo', 'di si', 'rock']
respond = ['Nema na čemu!', 'Np']


def timer(hr, mins=0, days=0):
    now = datetime.now()
    start = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
    end = timedelta(hours=hr, minutes=mins)
    delta = (end - start).seconds + days * 3600 * 24
    return delta


def check(value):
    if 'A' in value or 'B' in value:
        return 'Quiet'
    elif 'C' in value:
        return 'Small flare'
    elif 'M' in value:
        return 'Strong flare'
    elif 'X' in value:
        return 'Major flare'


def check2(value):
    if int(value) < 450:
        return 'Normal speed'
    elif 700 > int(value) >= 450:
        return 'Moderately high speed'
    elif 900 > int(value) <= 700:
        return 'High speed'
    elif int(value) >= 900:
        return 'Very high speed'


def sun_find():

    url1 = "https://www.spaceweatherlive.com/includes/live-data.php?object=solar_flare&lang=EN"
    url2 = 'https://www.spaceweatherlive.com/includes/live-data.php?object=Plasma_Speed&lang=EN'
    # payload = {}
    headers = {
        # 'PostmanRuntime/7.29.0',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Cache-Control': 'no-cache',
        'Host': 'www.spaceweatherlive.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    response = requests.get(url1, headers=headers)
    response2 = requests.get(url2, headers=headers)
    desc = ''
    print(str(response), str(response2))
    if str(response) == '<Response [200]>':
        data_dict = json.loads(response.text)
        curr_val = data_dict['val']
        max2 = data_dict['val2']
        max24 = data_dict['val24']

        soup = BeautifulSoup(curr_val, 'html.parser')
        curr_val = soup.find('div').text

        soup = BeautifulSoup(max2, 'html.parser')
        max2_val = soup.find('div').text

        soup = BeautifulSoup(max24, 'html.parser')
        max24_val = soup.find('div').text

        desc += f'Current value: **{curr_val}** - **{check(curr_val)}**\n2h max: **{max2_val}** - **{check(max2_val)}**\n24h max: **{max24_val}** - **{check(max24_val)}**'
    else:
        desc += f"Couldn't fetch data for solar flares."
    if str(response2) == '<Response [200]>':
        data_dict2 = json.loads(response2.text)

        spd_val = data_dict2['val']

        desc += f'\nSolar wind speed: **{spd_val}** km/sec - **{check2(spd_val)}**'
    else:
        desc += "\nCouldn't fetch data for solar wind speed."
    if '*' not in desc:
        desc = 'Sun data currently not available.'
    embed = discord.Embed(title='Solar Activity',
                          description=desc,
                          color=discord.Colour.orange())
    embed.set_thumbnail(url=r'https://i.ibb.co/D9ZrDT8/sun-1.png')
    return embed


def moon_find():
    url = 'https://www.timeanddate.com/moon/phases/'
    headers = {
        "User-Agent":
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }

    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    faza = soup.find(id="cur-moon-percent").get_text()
    parent = str(soup.find(id='qlook'))
    status = ''
    if 'Waxing' in parent:
        status = 'Moon is rising.'
    elif 'Waning' in parent:
        status = 'Moon is falling.'
    elif 'Full' in parent:
        status = 'Full Moon.'
    elif 'New' in parent:
        status = 'New Moon.'
    elif 'First' in parent:
        status = 'First Quarter.'
    elif 'Third' in parent:
        status = 'Third Quarter.'
    data = f"Moon's brightness: {faza}\n{status}"
    embed = discord.Embed(title='Moon\'s Phase',
                          description=data,
                          color=discord.Colour.blue())
    embed.set_thumbnail(url=r'https://i.imgur.com/CH7vNHi.png')
    return embed


class mirko(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=discord.Object(id=my_channel))
            await tree.sync()
            self.synced = True
        print(f"Logged in as {bot.user}")
        # await bot.change_presence(status=discord.Status.online, activity=discord.Game('discord.py'))

    async def setup_hook(self) -> None:
        self.ch_pr.start()
        self.bg_task = self.loop.create_task(self.reboot_task())
        self.astro_newsletter.start()
        # self.price_newsletter.start()

    async def reboot_task(self):
        await self.wait_until_ready()
        # print(f"Logged in as {bot.user}")
        f = open('database/reboot.txt', 'r+')
        # print(str(f.read()),f.read()=='',f.read())
        line = f.readline()
        if line != '':
            await bot.get_channel(int(line)).send('Reboot successful!')
            f.truncate(0)
        else:
            f.close()

    @tasks.loop(seconds=timer(hr=12))
    async def astro_newsletter(self):

        f = open('database/subbed_ch.txt', 'r')
        subbed = f.readlines()
        f.close()

        for cn in subbed:
            cn = int(cn[:len(cn) - 1])
            await bot.get_channel(cn).send(embed=moon_find())

            await bot.get_channel(cn).send(embed=sun_find())

    @astro_newsletter.before_loop
    async def before_astro_newsletter(self):
        await self.wait_until_ready()
        await asyncio.sleep(timer(hr=12))

    @tasks.loop(seconds=60)
    async def ch_pr(self):
        statuses = [
            f"on {len(bot.guilds)} servers", "discord.py", '/info for help',
            'Anime'
        ]
        status = random.choice(statuses)
        act = discord.Game(
            name=status) if statuses.index(status) < 2 else discord.Activity(
                type=discord.ActivityType.watching, name=status
        ) if statuses.index(status) == 3 else discord.Activity(
                type=discord.ActivityType.listening, name=status)
        await bot.change_presence(status=discord.Status.online, activity=act)

    @ch_pr.before_loop
    async def before_ch_pr(self):
        await self.wait_until_ready()

    @tasks.loop(seconds=900)
    async def anime_follow(self):

        with open('database/follow_dict.pkl', 'rb') as f:
            follow_dict, times = pickle.load(f)
        if times:
            index += 1
            index %= len(times)

            while index == 0 or index == len(times)-1 or (times[index][5] == times[index-1][5] and times[index][0].hour == times[index-1][0].hour and times[index][0].minute == times[index-1][0].minute):
                for user in follow_dict[times[index]]:
                    await discord.DMChannel.send(user, f"{times[2]} episode {times[1]}. was just released!")
                replacement = follow_dict[times[index]].copy()
                replacement[1] = str(int(follow_dict[times[index]][1])+1)
                follow_dict[replacement] = follow_dict.pop(
                    follow_dict[times[index]])
                times[times.times[index](
                    follow_dict[times[index]])] = replacement
                with open('database/follow_dict.pkl', 'wb') as f:
                    pickle.dump([follow_dict, times], f)
            time_left = timedelta(days=(times[index][1]+1)*7) - \
                (datetime.utcnow()-times[index][0])
            await asyncio.sleep(time_left.seconds+time_left.days*86400)

    @anime_follow.before_loop
    async def before_anime_follow(self):
        global index
        await self.wait_until_ready()
        with open('database/follow_dict.pkl', 'rb') as f:
            follow_dict, times = pickle.load(f)
        time_left = timedelta(days=(times[0][1]+1)*7) - \
            (datetime.utcnow()-times[0][0])
        await asyncio.sleep(time_left.seconds+time_left.days*86400)
        index = -1

    async def on_command_error(self, ctx, error):
        await ctx.replay(error, ephemeral=True)


bot = mirko()
tree = app_commands.CommandTree(bot)

# , guild=discord.Object(id=my_channel))


@tree.command(name='anime_list', description="Sends names and MAL URLs for known anime for easier search.")
async def self(interaction: discord.Interaction):
    msg = ""
    with open('database/anime_dict.pkl', 'rb') as f:
        anime_dict = pickle.load(f)
    if anime_dict:
        for item in anime_dict:
            msg += f"{item} - {anime_dict[item]}\n"
    else:
        msg = "Anime list is currently empty. Use /anime command to add anime to it."
    await interaction.response.send_message(msg)


@tree.command(name='anime', description="Sends data about given anime, use code, MAL URL or anime name to get data.")
async def self(interaction: discord.Interaction, code: str):
    await interaction.response.defer(ephemeral=False)
    with open('database/anime_dict.pkl', 'rb') as f:
        anime_dict = pickle.load(f)
    if not code.isdigit() and "myanimelist.net" not in code:
        code = [x.lower() for x in code.split()]
        for tag in anime_dict:
            tag2 = tuple([x.lower() for x in tag.split()])
            for word in code:
                if word in tag2:
                    code = anime_dict[tag]
                    break
            if word in tag2:
                break
    elif code.isdigit():
        code = "https://myanimelist.net/anime/"+code
    show = anime(code)
    try:
        show.fetch_data()

        anime_dict[show.name] = show.url
        with open('database/anime_dict.pkl', 'wb') as f:
            pickle.dump(anime_dict, f)
        # await interaction.response.send_message(show.__str__())
        out = discord.Embed(title=show.name,
                            description=show.__str__(),
                            color=genres[show.genre1])
        out.set_image(url=show.cover_url)
        # await interaction.response.send_message(embed=out)
        await interaction.followup.send(embed=out)
    except:
        await interaction.followup.send("Unsupported URL or anime.")


@tree.command(name='follow', description="Notifies you when a new episode of a given anime comes.")
async def self(interaction: discord.Interaction, code: str):
    await interaction.response.defer(ephemeral=False)
    with open('database/anime_dict.pkl', 'rb') as f:
        anime_dict = pickle.load(f)
    if not code.isdigit() and "myanimelist.net" not in code:
        code = [x.lower() for x in code.split()]
        for tag in anime_dict:
            tag2 = tuple([x.lower() for x in tag.split()])
            for word in code:
                if word in tag2:
                    code = anime_dict[tag]
                    break
            if word in tag2:
                break
    elif code.isdigit():
        code = "https://myanimelist.net/anime/"+code

    show = anime(code)
    # try:
    show.fetch_data()

    anime_dict[show.name] = show.url
    with open('database/anime_dict.pkl', 'wb') as f:
        print("pickling anime_dict", anime_dict, type(anime_dict))
        pickle.dump(anime_dict, f)
    if show.status == "Currently Airing":

        with open('database/follow_dict.pkl', 'rb') as f:
            follow_dict = pickle.load(f)
        with open('database/times.pkl', 'rb') as f:
            times = pickle.load(f)

        if show.time not in follow_dict:
            follow_dict[show.time] = []
        if interaction.user not in follow_dict[show.time]:
            follow_dict[show.time].append(interaction.user)

        def sorter(e):
            global time_left
            time_left = timedelta(days=(e[1]+1)*7) - \
                (datetime.utcnow()-e[0])
            return time_left.seconds+time_left.days*86400

        if show.time not in times:
            times.append(show.time)
            times.sort(key=sorter)
        print("pickling follow_dict", follow_dict,
              type(follow_dict), times, type(times))
        with open('database/follow_dict.pkl', 'wb') as f:
            pickle.dump(follow_dict, f)
        with open('database/times.pkl', 'wb') as f:
            pickle.dump(times, f)

        await interaction.followup.send(interaction.user, content=f"Successfully subsribed to {show.name}.")
    else:
        await interaction.followup.send(interaction.user, content=f"{show.name} anime is already finished.")
        # discord.DMchannel.send
    # except Exception as e:
    #    print(e)
    #    await interaction.followup.send("Unsupported URL or anime.")


@tree.command(name='anime_clear', description="Empties anime list.")
async def self(interaction: discord.Interaction):
    with open('database/anime_dict.pkl', 'rb') as f:
        anime_dict = pickle.load(f)
    anime_dict = {}
    with open('database/anime_dict.pkl', 'wb') as f:
        pickle.dump(anime_dict, f)
    await interaction.response.send_message("List deleted.")


@tree.command(name='ping', description='Sends bot\'s ping')
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(
        f'Pong! {round(bot.latency*1000)} ms')


@tree.command(name='send',
              description='Sends a message to a channel [DEV ONLY!]',
              guild=discord.Object(id=my_channel))
async def self(interaction: discord.Interaction, channel: int, message: str):
    if interaction.user.id in devs:
        try:
            channel = bot.get_channel(channel)
            await channel.send(message)
            await interaction.response.send_message('Message sent.')
        except:
            await interaction.response.send_message('Unknown channel.')
    else:
        interaction.response.send_message('Only devs can use this command.')


@tree.command(name='sun', description='Sends Sun\'s Activity')
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(embed=sun_find())


@tree.command(name='moon', description='Sends Moon\'s Phase')
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(embed=moon_find())


def block_read():
    with open('database/blocked.txt') as f:
        blocked = f.read().splitlines()
    return blocked


@tree.command(name='block',
              description='Blocks a user from using the bot [DEV ONLY!]')
async def self(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id in devs:
        try:
            # user = bot.get_user(user)
            f = open('database/blocked.txt', 'a+')
            f.seek(0)
            if str(user.id) + '\n' in f.readlines():
                f.close()
                await interaction.response.send_message('User already blocked.'
                                                        )
            else:
                f.write(str(user.id) + '\n')
                f.close()
                await interaction.response.send_message(
                    f'User <@{user.id}> blocked.')
        except:
            await interaction.response.send_message('Unknown user.')
    else:
        interaction.response.send_message('Only devs can use this command.')


@tree.command(name='unblock',
              description='Unblocks a user from using the bot [DEV ONLY!]')
async def self(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id in devs:
        try:
            # user = bot.get_user(user)
            f = open('database/blocked.txt', 'a+')
            f.seek(0)
            lines = f.readlines()
            f.close()
            # print(lines, str(user.id)+'\n')
            if str(user.id) + '\n' not in lines:
                await interaction.response.send_message(
                    f'User <@{user.id}> is already unblocked.')
            else:
                f = open('database/blocked.txt', 'w')
                for line in lines:
                    if line != str(user.id) + '\n':
                        f.write(line)
                f.close()
                await interaction.response.send_message(
                    f'User <@{user.id}> unblocked.')
        except Exception as e:
            # print(e)
            await interaction.response.send_message('Unknown user.')
    else:
        interaction.response.send_message('Only devs can use this command.')


@tree.command(
    name='subscribe',
    description='Subscribes a given/current channel to the astro newsletter')
async def self(interaction: discord.Interaction,
               channel: discord.TextChannel = None):
    if channel == None:
        cn_id = interaction.channel_id
    else:
        cn_id = channel.id
    f = open('database/subbed_ch.txt', 'r')
    subbed = f.readlines()
    f.close()

    if str(cn_id) + '\n' in subbed:
        await interaction.response.send_message(
            'This channel is already subscribed.')
    else:
        f = open('database/subbed_ch.txt', 'a')
        f.write(str(cn_id) + '\n')
        f.close()
        subbed.append(cn_id)
        await interaction.response.send_message('Successfully subscribed!')


@tree.command(
    name='unsubscribe',
    description='Unsubscribes a given/current channel from the astro newsletter'
)
async def self(interaction: discord.Interaction,
               channel: discord.TextChannel = None):
    if channel == None:
        cn_id = interaction.channel_id
    else:
        cn_id = channel.id
    f = open('database/subbed_ch.txt', 'r')
    subbed = f.readlines()
    f.close()

    if str(cn_id) + '\n' in subbed:
        subbed.remove(str(cn_id) + '\n')
        f = open('database/subbed_ch.txt', 'w')
        f.writelines(subbed)
        f.close()
        await interaction.response.send_message('Successfully unsubscribed!')
    else:
        await interaction.response.send_message(
            'This channel is already unsubscribed.')


@tree.command(
    name='dm',
    description='DMs a given user/sender with a custom/random message')
async def self(interaction: discord.Interaction,
               user: discord.User = None,
               message: str = None):
    if interaction.user.id not in block_read():
        if message == None:
            message = random.choice(dms)
        if user == None:
            user = interaction.user

        try:
            await discord.DMChannel.send(
                user, file=discord.File(rf'database/images/{message}'))

        except:
            await discord.DMChannel.send(user, content=message)
        await interaction.response.send_message('Message sent.')
    else:
        await interaction.response.send_message('You are blocked.')


@tree.command(name='img', description='Sends a random image from the database')
async def self(interaction: discord.Interaction):
    imgs = os.listdir(r'database/images')
    # imgs.remove('mauro.png')
    # imgs.remove('therock.gif')
    await interaction.response.send_message(
        file=discord.File(rf'database/images/{random.choice(imgs)}'))


@tree.command(name='quit',
              description='Shuts down the bot [DEV ONLY!]',
              guild=discord.Object(id=my_channel))
async def self(interaction: discord.Interaction):
    if interaction.user.id in devs:
        await interaction.response.send_message('Shutting down...')
        await bot.close()
    else:
        await interaction.response.send_message(
            'Only devs can use this command.')


@tree.command(name='reboot',
              description='Restarts the bot [DEV ONLY!]',
              guild=discord.Object(id=my_channel))
async def self(interaction: discord.Interaction):
    if interaction.user.id in devs:
        f = open('database/reboot.txt', 'w')
        f.write(str(interaction.channel_id))
        print(str(interaction.channel_id))
        f.close()
        await interaction.response.send_message('Restarting...')
        os.system("clear")
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        await interaction.response.send_message(
            'Only devs can use this command.')


@tree.command(name='dev_add',
              description='Marks a specific user as a bot\'s dev [DEV ONLY!]')
async def self(interaction: discord.Interaction, user: discord.User):
    if interaction.user.id in devs:
        try:
            f = open('database/devs.txt', 'a+')
            f.seek(0)
            if str(user.id) + '\n' in f.readlines():
                f.close()
                await interaction.response.send_message(
                    f'<@{user.id}> is already dev.')
            else:
                f.write(str(user.id) + '\n')
                f.close()
                await interaction.response.send_message(
                    f'Successfully added user <@{user.id}> as a dev.')
        except Exception as e:
            # print(e)
            await interaction.response.send_message('Unknown user.')
    else:
        await interaction.response.send_message(
            'Only devs can use this command.')


@tree.command(name='dev_remove',
              description='Removes a specific user as a bot\'s dev [DEV ONLY!]'
              )
async def self(interaction: discord.Interaction, user: discord.User):
    if interaction.user.id in devs:
        try:
            f = open('database/devs.txt', 'a+')
            f.seek(0)
            lines = f.readlines()
            f.close()
            # print(lines, str(user.id)+'\n')
            if str(user.id) + '\n' not in lines:
                await interaction.response.send_message(
                    f'User <@{user.id}> isn\'t dev.')
            else:
                f = open('database/blocked.txt', 'w')
                for line in lines:
                    if line != str(user.id) + '\n':
                        f.write(line)
                f.close()
                await interaction.response.send_message(
                    f'User <@{user.id}> removed as a dev.')
        except Exception as e:
            # print(e)
            await interaction.response.send_message('Unknown user.')
    else:
        interaction.response.send_message('Only devs can use this command.')


@tree.command(name='info', description='Sends information about the bot')
async def self(interaction: discord.Interaction):
    embed = discord.Embed(
        title='Mirko Bot Komande',
        description=' \n**-img**   \nšalje random sliku iz baze podataka \n\n  **-pong**  \n šalje Mirkov ping \n\n  **-dm user_id "poruka"**  \nšalje poruku u DM, ako nema id-a poruka se šalje pošiljatelju poruke \n\n  **-sun**  \n šalje podatke o trenutnoj Sunčevoj aktivnosti \n\n  **-moon**  \n šalje trenutnu osvjetljenost Mjeseca',
        color=discord.Colour.red(),
    )
    embed.set_author(
        name='Mirko Bot',
        icon_url='https://static.miraheze.org/hololivewiki/thumb/0/06/Album_Cover_Art_-_YoinoYoYoi.png/1200px-Album_Cover_Art_-_YoinoYoYoi.png'
    )
    embed.set_footer(text='For aditional information message Helix#3958.')
    embed.set_thumbnail(url=r'https://i.ibb.co/4TCmGnj/20220701-202610.png')
    await interaction.response.send_message(embed=embed)


@bot.event
async def on_message(message):
    if 'hvala' in message.content.lower() or 'thx' in message.content.lower():
        await message.channel.send('Nema na čemu!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("Unknown command.")


# keep_alive()
bot.run(token)
