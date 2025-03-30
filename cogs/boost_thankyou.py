import discord
from discord.ext import commands

class BoostThankYouCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.boost_role_id = 123456789012345678  # Ganti dengan ID role yang ingin diberikan

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # Mengecek apakah member baru saja memberikan boost
        if not before.premium_since and after.premium_since:
            boost_role = after.guild.get_role(self.boost_role_id)
            if boost_role:
                await after.add_roles(boost_role)
                
                # Membuat embed pesan terimakasih
                embed = discord.Embed(
                    title="Wah ada yang beli saham!",
                    description=f"Terimakasih {after.mention} sudah mau membeli dan memegang saham Burgeria!",
                    color=discord.Color.purple()
                )
                embed.set_thumbnail(url=after.avatar_url)
                embed.set_footer(text="dari seluruh board Burgeria", icon_url=after.guild.icon_url)

                # Mengirimkan embed ke channel tertentu (misal: channel dengan ID tertentu)
                thank_you_channel_id = 854711192073273375  # Ganti dengan ID channel yang ingin kamu gunakan
                thank_you_channel = after.guild.get_channel(thank_you_channel_id)
                if thank_you_channel:
                    await thank_you_channel.send(embed=embed)


    # This method runs when the cog is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'boost_thankyou.py loaded successfully.') 


async def setup(bot):
    await bot.add_cog(BoostThankYouCog(bot))
