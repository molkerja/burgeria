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
                    max_tokens=300  # Adjust token limit as needed
                )
                response_text = response.generations[0].text.strip()
                
                # Split the response into chunks that fit within Discord's message length limit
                def split_message(message, length=2000):
                    return [message[i:i+length] for i in range(0, len(message), length)]

                response_chunks = split_message(response_text)

                for chunk in response_chunks:
                    await message.channel.send(chunk)
            except Exception as e:
                await message.channel.send(f"Error fetching response from Cohere: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'chat_ai.py loaded successfully.')  

async def setup(bot):
    await bot.add_cog(ChatAICog(bot))
