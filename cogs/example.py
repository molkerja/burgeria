import discord
from discord.ext import commands

class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')

     # This method runs when the cog is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Example.py loaded successfully.')    

async def setup(bot):
    await bot.add_cog(ExampleCog(bot))
