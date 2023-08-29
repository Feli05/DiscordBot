import discord
from discord.ext import commands
import random
import requests
from pytube import YouTube
import spotipy
from asyncio import sleep
from spotipy.oauth2 import SpotifyClientCredentials
from config import DISCORD_TOKEN_RAW, GIPHY_API_KEY_RAW, SPOTIFY_CLIENT_ID_RAW, SPOTIFY_CLIENT_SECRET_RAW

#**********************************************

# Tokens used in program (Discord, GiphyAPI)

DISCORD_TOKEN = DISCORD_TOKEN_RAW
GIPHY_API_KEY = GIPHY_API_KEY_RAW
GIPHY_BASE_URL = 'https://api.giphy.com/v1/gifs/search'
SPOTIFY_ID = SPOTIFY_CLIENT_ID_RAW
SPOTIFY_SECRET = SPOTIFY_CLIENT_SECRET_RAW

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID_RAW, client_secret=SPOTIFY_CLIENT_SECRET_RAW))

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
    except Exception as e:
        print(e)

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

# ask bot for a list of commands
@bot.command()
async def commands(ctx):
    await ctx.send("""```Thanks for using this bot! \n\ncommands available at the moment: \n 
            - '!gif <topic>': sends a gif about a topic you choose. \n
            - 'pls jojo or pls jojos': sends a quote and a gif about JoJos Bizzare Adventure. \n 
            - 'pls dj khaled': sends a dj khaled quote and gif. \n
            - 'pls inspire me or pls inspire': sends a Rick Ross gif and an inspirational Vagabond quote. \n 
            - '!join': joins the voice channel that the user is in. \n
            - '!play <Youtube URL>': plays the requested song and sends information related to it if possible. \n 
            - '!pause': pauses the song. \n 
            - '!resume': resumes the song. \n 
            - '!stop': stops the music completely. \n\nMore features are being developed!```""")

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

# Spotify API functions ---

# parse the video title into song name and artist name if possible
def spotify_info(ctx, video_title, url):

    # Since the audio is now playing successfully, we can parse the title to extract the information to send a request to Spotipy
    if '-' in video_title and len(video_title.split('-')) == 2:

        # If this if returns True, it means the format is something like this: 'artist name - song name'
        artist_name = video_title.split('-')[0] # The artist name is usually the first part
        song_name = video_title.split('-')[1] # the song name is usually the second part

        # If the song name string has a parenthesis, we want to remove it
        if '(' in song_name:
            song_name = song_name.split('(')[0]

        # Now we can send a request to Spotify API with a song name and artist name
        song_info = spotify_search(song_name, artist_name) # Returns a list with information about the song

    # If the first conditional is not met, it means the title only contains the song name, so we directly check the parenthesis in the name
    elif '(' in video_title:
        song_name = video_title.split('(')[0] # Get the song name 
        song_info = spotify_search(song_name) # Send a request to Spotify API only with a track name

    # if song_info doesn't return Unknown it means that the request didn't have any problems
    if song_info[0] != 'Unknown':
        return (get_embed_msg(ctx, url, song_info, song_name))
    else:
        return ("Extra information about the requested song is not available.") 


# Main function that sends the API request 
def spotify_search(song_name, artist_name = 'Unknown'):
    
    # Request data from spotify
    if artist_name != 'Unknown':
        response = spotify.search(q= f'track: {song_name} artist: {artist_name}', limit=3, offset=0, type='track')
    else: 
        response = spotify.search(q= f'track: {song_name}', limit=3, offset=0, type='track')

    # check if the items we are looking for exists inside the nested dictionary
    # First, we check if the items list is not empty

    if response['tracks']['items']:
        info = response['tracks']['items'][0] # assign the list with the information we need to a variable to shorten its name

        # check if theres an album key in the items dict
        if 'album' in info:
            album_name = info['album']['name']
        else:
            album_name = 'Unknown'
        
        # check if theres an external urls key in the items dict
        if 'external_urls' in info:
            song_link = info['external_urls']['spotify']
        else:
            song_link = 'Unknown'
        
        # check if theres an images key inside the album dict 
        if 'album' in info and 'images' in info['album']:
            album_cover = info['album']['images'][0]['url']
        else:
            album_cover = 'Unknown'


    # return a list with the name of the album, link to the song on spotify and image of the album or single. 
    return [album_name, song_link, album_cover]


# Function that creates an embed message to display the information from the API request
def get_embed_msg(ctx, thumbnail_url, song_info, song_name):

    # Create embed object
    embed = discord.Embed(colour= discord.Color.purple(), title= f'Now playing {song_name}!', description=f'Album name: {song_info[0]}')

    # Set footer
    embed.set_footer(text= f'Song requested by {ctx.message.author}.')

    # Set author 
    embed.set_author(name= bot.user, url= 'https://github.com/Feli05/DiscordBot')
    
    # Set other components
    embed.set_thumbnail(url= 'https://i.postimg.cc/pXWmBpGJ/discord-bot-profile.jpg')
    embed.set_image(url= YouTube(thumbnail_url).thumbnail_url)

    return embed


# Prefix-command functions for controlling ---

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
    if voice_client:
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is currently not in any voice chats.")
    
# Play a song
@bot.command()
async def play(ctx, url):
    try:
        voice_client = ctx.message.guild.voice_client
        if not voice_client:
            await ctx.send("Bot is not connected to a voice channel.")
            return

        async with ctx.typing():
            print('About to create player for music.')
            # Creating a Youtube object and filtering the first audio only stream available
            yt = YouTube(url).streams.filter(only_audio=True).get_audio_only()
            print('Successfully created player!')
            # Stream the audio with options '-vn' which disable video so it focuses on audio only 
            voice_client.play(discord.FFmpegPCMAudio(yt.download(), options = '-vn'))
            # Send a message with information extracted from the Spotify metadata
            response = spotify_info(ctx, yt.title, url)
        
        # Send the embedded message
        await ctx.send(embed=response)

        # Wait for the music to stop playing
        while voice_client.is_playing():
            await sleep(1)

        # Send a last message
        await ctx.send(f'Song ended. Hope you enjoyed {ctx.message.author}!')

    except discord.ClientException:
        await ctx.send("Error: Bot is not connected to a voice channel.")

# stop playing a song
@bot.command()
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
    else:
        await ctx.send('Bot currently not playing a song.')

# resume playing a song
@bot.command()
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send('Song is already paused or there are none in queue.')

# pause a song
@bot.command()
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send('Bot currently not playing a song.')

#**********************************************

# Run commands

bot.run(DISCORD_TOKEN)