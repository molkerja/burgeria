import discord
from discord.ext import commands
import cohere
import configparser

class ChatAICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = configparser.ConfigParser()
        config.read('config.ini')

        try:
            self.api_key = config['client']['cohere_api_key']
            self.cohere_client = cohere.Client(self.api_key)
        except KeyError:
            raise Exception("API key for Cohere not found in config.ini")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content.startswith('--'):
            prompt = message.content[2:]

            try:
                response = self.cohere_client.generate(
                    model='command-r-plus',
                    prompt=prompt,
                    max_tokens=100
                )
                response_text = response.generations[0].text.strip()
                await message.channel.send(response_text)
            except Exception as e:
                await message.channel.send(f"Error fetching response from Cohere: {e}")

     # This method runs when the cog is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'chat_ai.py loaded successfully.')  

async def setup(bot):
    await bot.add_cog(ChatAICog(bot))
