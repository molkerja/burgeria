import discord
from discord.ext import commands
import asyncio

class ConfessionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['fess'])
    async def confess(self, ctx):
        if ctx.channel.type == discord.ChannelType.private:
            embed = discord.Embed(
                title='Mau ngomong apa khe!?',
                description='tapi jangan ngomong yg aneh biar ga ke ban sehari'
            )
            embed.set_footer(text='Bakalan batal kalo didiemin selama 10s')
            demand = await ctx.send(embed=embed)

            try:
                msg = await self.bot.wait_for(
                    'message',
                    timeout=10,
                    check=lambda message: message.author == ctx.author and message.channel == ctx.channel
                )
                if msg:
                    channel = self.bot.get_channel(894212908953792592)  # Ganti dengan ID channel yang sesuai
                    embed = discord.Embed(
                        description=f'{msg.content}'
                    )
                    embed.set_author(name='ada yang nitip pesen via DM, isinya')
                    embed.set_footer(text='silakan chat bgr!confess di DM.', icon_url='https://media.discordapp.net/attachments/860106193775230996/860106376051556372/secret-09.png?ex=668b183c&is=6689c6bc&hm=700ea411599457062e42077e6f99843f130a16d81c000720c24e80afec12f710&=&format=webp&quality=lossless&width=1058&height=1058')
                    await channel.send(embed=embed)
                    await demand.delete()
            
            except asyncio.TimeoutError:
                await ctx.send('cancelled', delete_after=5)
                await demand.delete()

        else:
            await ctx.reply('```diff\n- kirimnya ke DM lah, masa di sini, \njangan lupa pake command bgr!confess dulu```', mention_author=False)
        
     # This method runs when the cog is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Confess.py loaded successfully.')     

async def setup(bot):
    await bot.add_cog(ConfessionCog(bot))
