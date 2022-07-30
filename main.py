import discord
import random
import asyncio
import os
from keep_alive import keep_alive
import requests
from bs4 import BeautifulSoup
from discord import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
import sys
import json
from datetime import datetime, timedelta

client = commands.Bot(command_prefix='-')
slash = SlashCommand(client, sync_commands=True)
guilds = [guild.id for guild in client.guilds]


@slash.slash(
    name='test',
    description='Test command',
    guild_ids=guilds
)
async def _test(ctx: SlashContext):
    await ctx.send('Test')

admin = int(os.environ['admin_id'])
my_channel = int(os.environ['my_channel'])
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


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    f = open('database/reboot.txt', 'r+')
    # print(str(f.read()),f.read()=='',f.read())
    line = f.readline()
    if line != '':
        await client.get_channel(int(line)).send('Reboot successful!')
        f.truncate(0)
    else:
        f.close()


@client.event
async def ch_pr():
    await client.wait_until_ready()
    statuses = [
        f"on {len(client.guilds)} servers", "discord.py", '-info za pomoć'
    ]
    i = 0
    while not client.is_closed():
        if i < 3:
            status = statuses[i]
            await client.change_presence(activity=discord.Game(name=status))
            i += 1
        else:
            await client.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name="Anime"))
            i = 0
        await asyncio.sleep(30)


@client.listen('on_message')
async def message_checker(message):
    if 'hvala' in message.content or 'thx' in message.content:
        await message.channel.send('Nema na čemu!')


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("Unknown command.")


@client.command()
async def test(ctx, channel: discord.TextChannel = None):
    if channel != None:
        await channel.send(channel.id)


@client.command()
async def send(ctx, arg1, arg2):
    if ctx.author.id == admin:
        try:
            channel = client.get_channel(arg1)
            await channel.send(arg2)
            await ctx.send('Poruka poslana.')
        except:
            await ctx.send('Ne znam taj kanal.')


@client.command()
async def info(ctx):
    embed = discord.Embed(
        title='Mirko Bot Komande',
        description=' \n**-img**   \nšalje random sliku iz baze podataka \n\n  **-pong**  \n šalje Mirkov ping \n\n  **-dm user_id "poruka"**  \nšalje poruku u DM, ako nema id-a poruka se šalje pošiljatelju poruke \n\n  **-sun**  \n šalje podatke o trenutnoj Sunčevoj aktivnosti \n\n  **-moon**  \n šalje trenutnu osvjetljenost Mjeseca',
        color=discord.Colour.red(),
    )
    embed.set_thumbnail(
        url=r'https://i.ibb.co/4TCmGnj/20220701-202610.png')
    await ctx.send(embed=embed)


@client.command()
async def quit(ctx):
    if ctx.author.id == admin:
        await ctx.send('Odjavljujem se...')
        await client.close()


@client.command()
async def reboot(ctx):
    if ctx.author.id == admin:
        f = open('database/reboot.txt', 'w')
        f.write(str(ctx.channel.id))
        print(str(ctx.channel.id))
        f.close()
        await ctx.send('Restarting...')
        os.system("clear")
        os.execv(sys.executable, ['python'] + sys.argv)


@client.command()
async def img(ctx):
    imgs = os.listdir(r'database/images')
    # imgs.remove('mauro.png')
    # imgs.remove('therock.gif')
    await ctx.send(file=discord.File(r'database/images/' + random.choice(imgs))
                   )


@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)} ms')


@client.command()
async def dm(ctx, *args):
    stopdm = False
    cont = random.choice(dms)
    if len(args) != 0:
        for arg in args:
            try:
                int(arg)
                try:
                    user = await client.fetch_user(int(arg))
                except:
                    await ctx.send('Ne poznajem tog usera.')
                    stopdm = True
            except:
                cont = arg
    else:
        user = await client.fetch_user(ctx.author.id)
    if not stopdm:
        if cont == 'rock':
            await discord.DMChannel.send(
                user, file=discord.File(r'database/images/rock_sus.gif'))

        else:
            await discord.DMChannel.send(user, content=cont)
        await ctx.send('Poruka je poslana.')


@client.command()
async def sun(ctx):
    await ctx.send(embed=sun_find())


@client.command()
async def moon(ctx):
    await ctx.send(embed=moon_find())


@client.command()
async def price(ctx):
    res = price_checker()
    await client.get_channel(my_channel).send(embed=res[0])
    await client.get_channel(my_channel).send(embed=res[1])


@client.command()
async def subscribe(ctx, channel: discord.TextChannel = None):
    if channel == None:
        cn_id = ctx.channel.id
    else:
        cn_id = channel.id
    f = open('database/subbed_ch.txt', 'r')
    subbed = f.readlines()
    f.close()

    if str(cn_id) + '\n' in subbed:
        await ctx.send('This channel is already subscribed.')
    else:
        f = open('database/subbed_ch.txt', 'a')
        f.write(str(cn_id) + '\n')
        f.close()
        subbed.append(cn_id)
        await ctx.send('Successfully subscribed!')


@client.command()
async def unsubscribe(ctx, channel: discord.TextChannel = None):
    if channel == None:
        cn_id = ctx.channel.id
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
        await ctx.send('Successfully unsubscribed!')
    else:
        await ctx.send('This channel is already unsubscribed.')


@client.event
async def astro_newsletter():
    await client.wait_until_ready()
    await asyncio.sleep(timer(hr=12))
    f = open('database/subbed_ch.txt', 'r')
    subbed = f.readlines()
    f.close()

    for cn in subbed:
        cn = int(cn[:len(cn) - 1])
        await client.get_channel(cn).send(embed=moon_find())

        await client.get_channel(cn).send(embed=sun_find())


@client.event
async def price_newsletter():

    await client.wait_until_ready()

    await asyncio.sleep(timer(hr=9, days=1))

    res = price_checker()
    await client.get_channel(my_channel).send(embed=res[0])
    await client.get_channel(my_channel).send(embed=res[1])

token = str(os.environ['token'])
client.loop.create_task(ch_pr())
client.loop.create_task(astro_newsletter())
# client.loop.create_task(price_newsletter())
keep_alive()

try:
    client.run(token)
except:
    os.system("kill 1")
