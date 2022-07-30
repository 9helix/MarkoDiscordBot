import discord
from discord.ext import commands
from discord import app_commands
from discord.ext import tasks
import random
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import json
import os
import sys
import asyncio
from keep_alive import keep_alive

bot = commands.Bot(command_prefix='-', intents=discord.Intents.all())

admin = int(os.environ['admin_id'])
my_channel = int(os.environ['my_channel'])
token = str(os.environ['token'])

space = '<:space:988547133902819378>'
ojou = '<:ojou:990313694204395540>'

dms = ['bok', 'yo', 'waddup', 'di si', 'rock']
respond = ['Nema na čemu!', 'Np']


def price_checker():
    url = "https://www.links.hr/hr/monitor-23-8-aoc-24g2u-fhd-ips-144hz-1ms-250cd-m2-80-000-000-1-zvucnici-crni-100300456"
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"}

    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    with open('database/price_log.txt') as f:
        l = f.readlines()
        if l != []:
            line = l[len(l)-1]
            last_price = line[:len(line)-1]
        else:
            last_price = '0,00 kn'
    price = soup.find(
        'span', {'class': 'price-value-94695'}).get_text().strip()
    name = soup.find('h1', itemprop="name").get_text().strip()

    price = price[:len(price)-5]+','+price[len(price)-5:]
    value = float(price.replace(',', '.').replace(
        '.', '', 1)[:len(price)-3])
    last_value = float(last_price.replace(
        ',', '.').replace('.', '', 1)[:len(last_price)-3])

    if value < last_value:
        result = f'Price decreased! Before: **{last_price}** Now: **{price}**'
        print(result)
        f = open('database/price_log.txt', 'a')
        f.write(str(price)+'\n')
        f.close()
    elif value > last_value:
        f = open('database/price_log.txt', 'a')
        f.write(str(price)+'\n')
        f.close()
        result = f'Price increased! Before: **{last_price} Now: **{price}**'
        print(result)
    else:
        result = f'Price unchanged! **{price}**'
        print(result)
    rijeka = soup.find('a', {'href': '/hr/links-rijeka'}
                       ).parent.find_next_siblings('td')
    web = soup.find('td', {'class': 'warehouse'},
                    string=' WEBSHOP').find_next_siblings('td')
    for i in rijeka:
        i = BeautifulSoup(str(i), 'html.parser')

        if i.find('span', {'class': 'circle active'}) != None:
            ri = f'RIJEKA{space*1}'
            if i.find('td', {'class': 'warehouseAvailable'}) != None:
                ri += f':green_circle:{space*1}**AVAILABLE**'
            elif i.find('td', {'class': 'warehouseOnRequest'}) != None:
                ri += f':orange_circle:{space*1}**ON REQUEST**'
            elif i.find('td', {'class': 'warehouseNotAvailable'}) != None:
                ri += f':red_circle:{space*1}**NOT AVAILABLE**'
            break
    for i in web:
        i = BeautifulSoup(str(i), 'html.parser')
        if i.find('span', {'class': 'circle active'}) != None:
            we = f'WEBSHOP{space*1}'
            if i.find('td', {'class': 'warehouseAvailable'}) != None:
                we += f':green_circle:{space*1}**AVAILABLE**'
            elif i.find('td', {'class': 'warehouseOnRequest'}) != None:
                we += f':orange_circle:{space*1}**ON REQUEST**'
            elif i.find('td', {'class': 'warehouseNotAvailable'}) != None:
                we += f':red_circle:{space*1}**NOT AVAILABLE**'
            break
    # print(we)
    # print(ri)
    embed = discord.Embed(
        title=name, url=url, color=discord.Colour.teal(), description=result+'\n'+we+'\n'+ri)
    embed.set_thumbnail(url='https://i.ibb.co/HTf39nf/tag.png')

    url = "https://edigital.hr/monitor/aoc-24g2u-fullhd-ips-144hz-gamer-led-monitor-p691923"
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    price = soup.find('strong', {'class': 'price price--large'}).get_text()
    stat = soup.find('span', {'class': 'stock-info__text'})
    name = soup.find('h1', {'class': 'main-title'}).get_text()
    if stat != None:
        if stat.get_text() == 'na zalihi':
            stat = ':green_circle: na zalihi'
        else:
            stat = ':orange_circle:'+stat.get_text()
    else:
        stat = ':red_circle: nije više dobavljiv'
    embed2 = discord.Embed(
        title=name, url=url, color=discord.Colour.teal(), description=f'**{price}**\n{stat}')
    embed2.set_thumbnail(url='https://i.ibb.co/HTf39nf/tag.png')
    return embed, embed2


def timer(hr, min=0, days=0):
    now = datetime.now()
    start = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
    end = timedelta(hours=hr, minutes=min)
    delta = (end - start).seconds+days*3600*24
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
    #payload = {}
    headers = {
        # 'PostmanRuntime/7.29.0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
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
    embed = discord.Embed(title='Moon Status',
                          description=data,
                          color=discord.Colour.blue())
    embed.set_thumbnail(url=r'https://i.imgur.com/CH7vNHi.png')
    return embed


class mirko(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await tree.sync(guild=discord.Object(id=913678455223251004))
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
        #print(f"Logged in as {bot.user}")
        f = open('database/reboot.txt', 'r+')
        # print(str(f.read()),f.read()=='',f.read())
        line = f.readline()
        if line != '':
            await bot.get_channel(int(line)).send('Reboot successful!')
            f.truncate(0)
        else:
            f.close()

    @tasks.loop(seconds=timer(hr=9, days=1))
    async def price_newsletter(self):

        f = open('database/subbed_ch.txt', 'r')
        subbed = f.readlines()
        f.close()

        for cn in subbed:
            cn = int(cn[:len(cn) - 1])
            await bot.get_channel(cn).send(embed=moon_find())

            await bot.get_channel(cn).send(embed=sun_find())

    @price_newsletter.before_loop
    async def before_price_newsletter(self):
        await self.wait_until_ready()
        await asyncio.sleep(timer(hr=9, days=1))

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

    @tasks.loop(seconds=30)
    async def ch_pr(self):
        statuses = [
            f"on {len(bot.guilds)} servers", "discord.py", '-info for help', 'anime'
        ]
        status = random.choice(statuses)
        act = discord.Game(name=status) if statuses.index(status) < 2 else discord.Activity(type=discord.ActivityType.watching,
                                                                                            name=status) if statuses.index(status) == 3 else discord.Activity(type=discord.ActivityType.listening, name=status)
        await bot.change_presence(status=discord.Status.online, activity=act)

    @ch_pr.before_loop
    async def before_ch_pr(self):
        await self.wait_until_ready()


bot = mirko()
tree = app_commands.CommandTree(bot)


@tree.command(name='ping', description='Sends bot\'s ping', guild=discord.Object(id=913678455223251004))
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(f'Pong! {round(bot.latency*1000)} ms')


@tree.command(name='send', description='Sends a message to a channel [DEV ONLY]', guild=discord.Object(id=913678455223251004))
async def self(interaction: discord.Interaction, channel: int, message: str):
    if interaction.user.id == admin:
        try:
            channel = bot.get_channel(channel)
            await channel.send(message)
            await interaction.response.send_message('Message sent.')
        except:
            await interaction.response.send_message('Unknyown channel.')
    else:
        interaction.response.send_message('Only devs can use this command.')


@tree.command(name='sun', description='Sends Sun Status', guild=discord.Object(id=913678455223251004))
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(embed=sun_find())


@tree.command(name='moon', description='Sends Moon Status', guild=discord.Object(id=913678455223251004))
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(embed=moon_find())


@tree.command(name='price', description='Sends product\'s current price', guild=discord.Object(id=913678455223251004))
async def self(interaction: discord.Interaction):
    res = price_checker()
    await bot.get_channel(my_channel).send(embed=res[0])
    await bot.get_channel(my_channel).send(embed=res[1])


@tree.command(name='block', description='Blocks a user from using the bot [DEV ONLY]', guild=discord.Object(id=913678455223251004))
async def self(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id == admin:
        try:
            #user = bot.get_user(user)
            f = open('database/blocked.txt', 'a+')
            f.seek(0)
            if str(user.id)+'\n' in f.readlines():
                await interaction.response.send_message('User already blocked.')
            else:
                f.write(str(user.id) + '\n')
                f.close()
                await interaction.response.send_message(f'User <@{user.id}> blocked.')
        except:
            await interaction.response.send_message('Unknown user.')
    else:
        interaction.response.send_message('Only devs can use this command.')


@tree.command(name='unblock', description='Unblocks a user from using the bot [DEV ONLY]', guild=discord.Object(id=913678455223251004))
async def self(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id == admin:
        try:
            #user = bot.get_user(user)
            f = open('database/blocked.txt', 'a+')
            f.seek(0)
            lines = f.readlines()
            f.close()
            #print(lines, str(user.id)+'\n')
            if str(user.id)+'\n' not in lines:
                await interaction.response.send_message(f'User <@{user.id}> is already unblocked.')
            else:
                f = open('database/blocked.txt', 'w')
                for line in lines:
                    if line != str(user.id) + '\n':
                        f.write(line)
                f.close()
                await interaction.response.send_message(f'User <@{user.id}> unblocked.')
        except Exception as e:
            # print(e)
            await interaction.response.send_message('Unknown user.')
    else:
        interaction.response.send_message('Only devs can use this command.')


@tree.command(name='subscribe', description='Subscribes a given/current channel', guild=discord.Object(id=913678455223251004))
async def self(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if channel == None:
        cn_id = interaction.channel_id
    else:
        cn_id = channel.id
    f = open('database/subbed_ch.txt', 'r')
    subbed = f.readlines()
    f.close()

    if str(cn_id) + '\n' in subbed:
        await interaction.response.send_message('This channel is already subscribed.')
    else:
        f = open('database/subbed_ch.txt', 'a')
        f.write(str(cn_id) + '\n')
        f.close()
        subbed.append(cn_id)
        await interaction.response.send_message('Successfully subscribed!')


@tree.command(name='unsubscribe', description='Unsubscribes a given/current channel', guild=discord.Object(id=913678455223251004))
async def self(interaction: discord.Interaction, channel: discord.TextChannel = None):
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
        await interaction.response.send_message('This channel is already unsubscribed.')


@tree.command(name='dm', description='DMs a given user/sender with a custom/random message', guild=discord.Object(id=913678455223251004))
async def self(interaction: discord.Interaction, user: discord.User = None, message: str = None):
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


@tree.command(name='img', description='Sends a random image from the database', guild=discord.Object(id=913678455223251004))
async def self(interaction: discord.Interaction):
    imgs = os.listdir(r'database/images')
    # imgs.remove('mauro.png')
    # imgs.remove('therock.gif')
    await interaction.response.send_message(file=discord.File(rf'database/images/{random.choice(imgs)}')
                                            )


@tree.command(name='quit', description='Shuts down the bot [DEV ONLY]', guild=discord.Object(id=913678455223251004))
async def self(interaction: discord.Interaction):
    if interaction.user.id == admin:
        await interaction.response.send_message('Shutting down...')
        await bot.close()
    else:
        await interaction.response.send_message('Only devs can use this command.')


@tree.command(name='reboot', description='Restarts the bot [DEV ONLY]', guild=discord.Object(id=913678455223251004))
async def self(interaction: discord.Interaction):
    if interaction.user.id == admin:
        f = open('database/reboot.txt', 'w')
        f.write(str(interaction.channel_id))
        print(str(interaction.channel_id))
        f.close()
        await interaction.response.send_message('Restarting...')
        os.system("clear")
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        await interaction.response.send_message('Only devs can use this command.')


@tree.command(name='info', description='Sends infromation about the bot', guild=discord.Object(id=913678455223251004))
async def self(interaction: discord.Interaction):
    embed = discord.Embed(
        title='Mirko Bot Komande',
        description=' \n**-img**   \nšalje random sliku iz baze podataka \n\n  **-pong**  \n šalje Mirkov ping \n\n  **-dm user_id "poruka"**  \nšalje poruku u DM, ako nema id-a poruka se šalje pošiljatelju poruke \n\n  **-sun**  \n šalje podatke o trenutnoj Sunčevoj aktivnosti \n\n  **-moon**  \n šalje trenutnu osvjetljenost Mjeseca',
        color=discord.Colour.red(),
    )
    embed.set_author(
        name='Mirko Bot', icon_url='https://static.miraheze.org/hololivewiki/thumb/0/06/Album_Cover_Art_-_YoinoYoYoi.png/1200px-Album_Cover_Art_-_YoinoYoYoi.png')
    embed.set_footer(text='For aditional information message Helix#3958')
    embed.set_thumbnail(
        url=r'https://i.ibb.co/4TCmGnj/20220701-202610.png')
    await interaction.response.send_message(embed=embed)


@bot.event
async def on_message(message):
    if 'hvala' in message.content.lower() or 'thx' in message.content.lower():
        await message.channel.send('Nema na čemu!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("Unknown command.")
keep_alive()
bot.run(token)
