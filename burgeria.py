import discord
import os
import io
import aiohttp
from discord.ext import commands, tasks
from discord import app_commands
from configparser import SafeConfigParser
from PIL import Image, ImageDraw, ImageFont



# Read the configuration file
config = SafeConfigParser()
config.read('./config.ini')

# Extract configuration values
token = config['client']['token']
prefix = str(config['client']['prefix'])
guild_id = int(config['client']['guild_id'])  # Assuming guild_id is configured in config.ini
message_id_waiter = int(config['client']['message_id_waiter'])  # Message ID where users react to get the role
emoji_waiter = '📄'  # Emoji users will react with to get the role (thumbs up in this case)
role_id_waiter = int(config['client']['role_id_waiter'])  # Role ID to assign when users react to the message
#openai.api_key = config['client']['openai_api_key']
welcome_channel_id = int(config['client']['welcome_channel_id'])
member_count_channel_id = int(config['client']['member_count_channel_id'])

# Create the bot instance
bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())
intents = discord.Intents.default()
intents.members = True  # Enable the members intent

# Load cogs
async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')  # Await the load_extension coroutine
                print(f'Loaded cog: {filename}')
            except Exception as e:
                print(f'Failed to load cog {filename}: {e}')

@bot.event
async def on_member_join(member):
    print(f'New member joined: {member.name}')
    await send_welcome_message(member)
    await update_member_count_channel()

@bot.event
async def on_member_remove(member):
    print(f'Member left: {member.name}')
    await update_member_count_channel()

async def send_welcome_message(member):
    channel = bot.get_channel(welcome_channel_id)
    if channel:
        embed = discord.Embed(
            description=f"Selamat datang di Kantor Burgeria {member.mention}, Silahkan daftar loker dahulu di <#854375682552627200>",
            color=322677
        )
        # Set the server icon as the thumbnail
        embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else discord.Embed.Empty)
        
        # Set the author to the server name and icon
        embed.set_author(name=member.guild.name, icon_url=member.guild.icon.url if member.guild.icon else discord.Embed.Empty)
        
        # Set the footer to the member's name and avatar
        embed.set_footer(text=member.name, icon_url=member.display_avatar.url)
        await member.send(embed=embed)
        await channel.send(embed=embed)
        print(f'Welcome message sent to {member.name} in {channel.name}')
    else:
        print(f'Channel with ID {welcome_channel_id} not found')

async def update_member_count_channel():
    guild = bot.guilds[0]  # Assumes the bot is in one guild only
    member_count = len(guild.members) - 1  # Exclude the bot itself
    channel = bot.get_channel(member_count_channel_id)
    print(f'👥 | {channel} Karyawan')
    if channel:
        new_name = f'👥 | {member_count} Karyawan'
        await channel.edit(name=new_name)
        print(f'Updated member count channel to: {new_name}')
    else:
        print(f'Channel with ID {member_count_channel_id} not found')

# Task to update activity status with member count
@tasks.loop(minutes=5)  # Update every 5 minutes (adjust as needed)
async def update_member_count():
    guild = bot.get_guild(guild_id)
    if guild:
        member_count = len(guild.members) - 1  # Exclude the bot itself
        activity = discord.Activity(type=discord.ActivityType.watching, name=f'{member_count} karyawan Burgeria')
        await bot.change_presence(activity=activity)

# Basic on_ready event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    update_member_count.start()

# Add Waiter role when react the message and send employee card
@bot.event
async def on_raw_reaction_add(payload):
    print(f"Emoji from payload: {payload.emoji}")
    print(f"Emoji waiter configured: {emoji_waiter}")
    
    if payload.message_id == message_id_waiter and str(payload.emoji) == emoji_waiter:
        guild = bot.get_guild(guild_id)
        if guild:
            member = guild.get_member(payload.user_id)
            if member:
                role = guild.get_role(role_id_waiter)
                if role:
                    try:
                        await member.add_roles(role)
                        # Resize and edit the employee card image
                        img = Image.open("./photo/id-card-blanko-02.png")
                        img = img.resize((1033, 631))  # Resize the image if necessary
                        
                        draw = ImageDraw.Draw(img)
                        author = format(member.top_role)
                        author = author[2:]  # Assuming you trim the role correctly as per your use case
                        font = ImageFont.truetype("./fonts/Handwritten_Nat29_Font.ttf", 60)
                        ttd = ImageFont.truetype("./fonts/Mix Palmer.ttf", 60)
                        
                        # Example text drawing
                        draw.text((255, 196), "BGR{}".format(member.id), (230, 233, 207), font=font)  # User ID with prefix
                        draw.text((403, 275), "{}".format(member.display_name), (38, 52, 112), font=font)  # Member's nickname
                        draw.text((403, 325), f"{author}", (38, 52, 112), font=font)  # Top role
                        draw.text((400, 370), "{}".format(member.joined_at.strftime("%d %b %Y")), (38, 52, 112), font=font)  # Join date
                        draw.text((832, 562), "{}".format(member.display_name), (164, 30, 36), anchor="ms", font=ttd)
                        
                        try:
                            # Fetch member's avatar and paste it onto the image
                            avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
                            async with aiohttp.ClientSession() as session:
                                async with session.get(avatar_url) as response:
                                    if response.status == 200:
                                        buffer_avatar = io.BytesIO(await response.read())
                                        avatar_image = Image.open(buffer_avatar)
                                        avatar_image = avatar_image.resize((177, 177))  # Resize avatar if needed
                                        img.paste(avatar_image, (68, 306))  # Adjust coordinates to position avatar
                        except Exception as e:
                            print(f'Error fetching or processing avatar: {e}')
                        
                        # Save the modified image
                        img.save("kartu-karyawan-baru.png")
                        
                        # Send the image to a specific channel
                        await bot.get_channel(854711192073273375).send(file=discord.File("kartu-karyawan-baru.png"))
                        
                        print(f'Added role {role.name} to {member.display_name}')
                    except discord.Forbidden:
                        print(f'Failed to add role {role.name} to {member.display_name}: Permission denied')

# Remove Waiter role when un-react the message
@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id == message_id_waiter:
        guild = bot.get_guild(guild_id)  # Fetch guild using cached data
        if guild:
            member = guild.get_member(payload.user_id)  # Fetch member using cached data
            if member:
                role = guild.get_role(role_id_waiter)
                if role and role in member.roles:
                    try:
                        await member.remove_roles(role)
                        print(f'Removed role {role.name} from {member.display_name}')
                    except discord.Forbidden:
                        print(f'Failed to remove role {role.name} from {member.display_name}: Permission denied')


# Load the cogs and run the bot
async def main():
    async with bot:
        await load_cogs()
        await bot.start(token)

import asyncio
asyncio.run(main())
