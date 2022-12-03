import discord
from discord.ext import commands


class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = """
```
General commands:
help - displays all the available commands
p <keywords> - plays the first result from youtube
q - displays the current music queue
skip - skips the current song
clear - stops the music and clears the queue
leave - stops the music and leaves the voice channel
resume - resumes the current song
```
"""
        self.text_channel_text = []


"""
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_Text.append(channel)
        await self.send_to_all(self.help_message)

    async def send_to_all(self, msg):
        for text_channel in self.text_channel_text:
            await text_channel.send(msg)"""


@commands.command(name="help", help="Displays all the available commands")
async def help(self, ctx):
    await ctx.send(self.help_message)
