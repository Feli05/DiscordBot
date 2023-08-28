import discord
from discord.ext import commands
import random
import requests
import youtube_dl
import asyncio
from config import DISCORD_TOKEN_RAW, GIPHY_API_KEY_RAW

#**********************************************

# Tokens used in program (Discord, GiphyAPI)

DISCORD_TOKEN = DISCORD_TOKEN_RAW
GIPHY_API_KEY = GIPHY_API_KEY_RAW
GIPHY_BASE_URL = 'https://api.giphy.com/v1/gifs/search'

#**********************************************

# Declare the bot and its command prefix 

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Boot the bot

@bot.event
async def on_ready():
    print("Bot Ready")
    try:
        synced = await bot.tree.sync()
        print("Commands Synced!")
    except:
        print(Exception)

#**********************************************

# List of quote arrays

Vagabond_quotes = ["Preoccupied with a single leaf, you won’t see the tree… preoccupied with a single tree, you’ll miss the entire forest.", 
" You must understand that there is more than one path to the top of the mountain.", "Resentment and complaint are appropriate neither for oneself nor others.", 
"Think lightly of yourself and deeply of the world.", "Immature strategy is the cause of grief."]

JoJo_quotes = ["Arrivederci.", "Welcome... To the True Man’s World.", "Being human means having limits. I’ve learned something. The more carefully you scheme, the more unexpected events come along.",
"What is courage? Courage is owning your fear!", "Loneliness will make a man hollow.", "Humans ought to lead a life that leads them to heaven. This is what makes humans beautiful.",
"The shortest path was a detour.", "Presumptions are more terrifying than anything else. Especially when you are under the impression that your strengths and abilities are impressive."]

DJKhaled_quotes = ["Budget approved.", "Did the Drake vocals come in yet.", "Call me Asparagus", "Tell 'em to bring the yacht out.", "Tell 'em to bring out the whole ocean.", 
"And perhaps what is this.", "Let's go golfing!", "Life...is Roblox", " They ain't believe in us... GOD DID", "Have you ever played rugby.", "Tell 'em to bring out the lobster."]

#**********************************************

# Prefix-command functions

# Simple Hello command
@bot.command()
async def hello(ctx):
    await ctx.reply("Hello")

# Command that asks user for GIF topic and requests URL from GiphyAPI
@bot.command()
async def gif(ctx, input):
    # Specify parameters for request and send it
    params = {'api_key': GIPHY_API_KEY, 'q': input, 'rating': 'g', 'lang': "en"}
    response = requests.get(GIPHY_BASE_URL, params=params)

    #Parse the json request and choose random url 
    parsed_data = response.json()['data']
    random_data = random.choice(parsed_data)
    gif_url = random_data['images']['original']['url']

    #send the url to the discord channel
    await ctx.send(gif_url)

#**********************************************

# Text-based functions

@bot.event
async def on_message(message):
    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel.name) 
    
    # Keep track of chat inside the terminal
    print(f'{username}: {user_message} ({channel})')

    if message.author == bot.user: 
        return # So it doesn't reply to its own messages
    
    if "pls dj khaled" == user_message.lower():
        response = random.choice(DJKhaled_quotes)
        await message.channel.send(response)
        await gif(message.channel, "DJ Khaled")
     
    elif "pls jojo" == user_message.lower() or "pls jojos" == user_message.lower():
        response = random.choice(JoJo_quotes)
        await message.channel.send(response)
        await gif(message.channel, "JoJos Anime")
  
    elif "pls inspire" == user_message.lower() or "pls inspire me" == user_message.lower():
        response = random.choice(Vagabond_quotes)
        await message.channel.send(response)
        await gif(message.channel, "Rick Ross")

    elif "pls " in user_message:
            await message.channel.send("Not a valid command. Try using '!help'.")


    await bot.process_commands(message)

#**********************************************

# Audio commands

# Supress error noises
youtube_dl.utils.bug_reports_message = lambda: ''

# Youtube-DL format config
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', 
}

# ffmpeg config
ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        if stream:
            return cls(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data)
        else:
            filename = ytdl.prepare_filename(data)
            return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# Prefix-command functions for controlling

# Join the same VC as the user requesting it
@bot.command()
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel.")
    else: 
        await ctx.message.author.voice.channel.connect()

# Leave the VC
@bot.command()
async def leave(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is currently not in any voice chats.")
    
# Play a song
@bot.command()
async def play(ctx, url):
    try:
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if not voice_client:
            await ctx.send("Bot is not connected to a voice channel.")
            return

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=bot.loop)
            voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {player.title}')
    except discord.ClientException:
        await ctx.send("Error: Bot is not connected to a voice channel.")
    except youtube_dl.DownloadError:
        await ctx.send("Error downloading or playing the provided URL")


# Stop playing a song
@bot.command()
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing a song currently.")


#**********************************************


# Run commands

bot.run(DISCORD_TOKEN)