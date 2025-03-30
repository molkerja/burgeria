import discord
from discord.ext import commands, tasks
import feedparser
from discord_webhook import DiscordWebhook, DiscordEmbed
from bs4 import BeautifulSoup


class RSSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rss_feed_url = "https://steamcommunity.com/groups/freegamesfinders/rss/"  # Ganti dengan URL RSS feed Anda
        self.webhook_url = "https://discord.com/api/webhooks/855815600180690955/hLG33zgDERaE0r98gQhRj0veD9pW04q8tho97WpATKRVO3Ee-Usf06INSOCTkZbR9GuC"  # Ganti dengan URL webhook Anda
        self.role_id_to_mention = 903276473413140490  # Ganti dengan ID role yang ingin di-mention
        self.last_entry_id = None
        self.check_feed.start()

    def cog_unload(self):
        self.check_feed.cancel()

    @tasks.loop(minutes=5)  # Cek feed setiap 5 menit
    async def check_feed(self):
        feed = feedparser.parse(self.rss_feed_url)
        if not feed.entries:
            return

        new_entry = feed.entries[0]
        if self.last_entry_id != new_entry.id:
            self.last_entry_id = new_entry.id
            await self.send_webhook_message(new_entry)

    async def send_webhook_message(self, entry):
        # Uraikan HTML dalam deskripsi dan konversi hyperlink ke format markdown
        soup = BeautifulSoup(entry.summary, 'lxml')
        clean_description = ''
        for element in soup.descendants:
            if element.name == 'a':
                # Konversi hyperlink ke format markdown dengan menambahkan newline setelahnya
                clean_description += f"[{element.text}]({element['href']})\n"
            elif element.name is None:
                clean_description += element
            elif element.name == 'br':
                clean_description += '\n'
            elif element.name == 'p':
                clean_description += '\n\n'

        # Buat embed
        embed = DiscordEmbed(title=entry.title, url=entry.link, description=clean_description.strip(), color='03b2f8')
        embed.set_author(name="Bergame Gratisan Ria")
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/855815600180690955/f376f99c2392bb4bd04cc66029cc8c16.png?size=160")  # Ganti dengan URL avatar akun webhook
        embed.set_timestamp()

        # Buat webhook dan tambahkan embed
        webhook = DiscordWebhook(url=self.webhook_url, content=f"<@&{self.role_id_to_mention}>")  # Mention role
        webhook.add_embed(embed)

        response = webhook.execute()
        print(f'Sent embed webhook message: {response.status_code}')

    @check_feed.before_loop
    async def before_check_feed(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(RSSCog(bot))