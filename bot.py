import discord
from discord.ext import commands
import random
import requests
from pytube import YouTube, Search
import spotipy
from asyncio import sleep
from spotipy.oauth2 import SpotifyClientCredentials
from config import DISCORD_TOKEN_RAW, GIPHY_API_KEY_RAW, SPOTIFY_CLIENT_ID_RAW, SPOTIFY_CLIENT_SECRET_RAW
from bot_extra import DJKhaled_quotes, Vagabond_quotes, JoJo_quotes, commands_help, music_help, art_help

#**********************************************

# Tokens used in program (Discord, GiphyAPI)

DISCORD_TOKEN = DISCORD_TOKEN_RAW
GIPHY_API_KEY = GIPHY_API_KEY_RAW
GIPHY_BASE_URL = 'https://api.giphy.com/v1/gifs/search'
WAIFU_BASE_URL = 'https://api.waifu.im/search'
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

# Help commands

# ask bot for a general overview of commands
@bot.command()
async def commands(ctx):

    # Create an embed object
    embed = discord.Embed(colour= discord.Color.orange(), type='rich', title='Joestar Bot command list!', description='For further help, please do ``!<command>``')
    # Set author 
    embed.set_author(name=bot.user, url='https://github.com/Feli05/DiscordBot')
    # Set embed thumbnail
    embed.set_thumbnail(url='https://i.postimg.cc/pXWmBpGJ/discord-bot-profile.jpg')
    # Set the main text on the embed
    embed.add_field(name='commands available', value=commands_help, inline=True)
    # Set footer text
    embed.set_footer(text=f'Requested by: {ctx.message.author}')
    
    await ctx.send(embed=embed)


# Detailed help about music commands
@bot.command()
async def music(ctx):

    # Create an embed object
    embed = discord.Embed(colour= discord.Color.orange(), type= 'rich', title= 'Music commands help!', description='Detailed help for all the music commands available on the Joestar bot.')
    # Set author 
    embed.set_author(name= bot.user, url= 'https://github.com/Feli05/DiscordBot')
    # Set embed thumbnail
    embed.set_thumbnail(url= 'https://i.postimg.cc/pXWmBpGJ/discord-bot-profile.jpg')
    # Set the main text on the embed
    embed.add_field(name='commands available', value=music_help, inline=True)
    # Set footer text
    embed.set_footer(text=f'Requested by: {ctx.message.author}')
    
    await ctx.send(embed=embed)


# Detailed help about art commands
@bot.command()
async def art(ctx):

    # Create an embed object
    embed = discord.Embed(colour= discord.Color.orange(), type= 'rich', title= 'Art commands help!', description='Detailed help for all the art commands available on the Joestar bot.')
    # Set author 
    embed.set_author(name= bot.user, url= 'https://github.com/Feli05/DiscordBot')
    # Set embed thumbnail
    embed.set_thumbnail(url= 'https://i.postimg.cc/pXWmBpGJ/discord-bot-profile.jpg')
    # Set the main text on the embed
    embed.add_field(name='commands available', value=art_help, inline=True)
    # Set footer text
    embed.set_footer(text=f'Requested by: {ctx.message.author}')
    
    await ctx.send(embed=embed)
    
#**********************************************

# Command-based functions

# Command that asks user for GIF topic and requests URL from GiphyAPI
@bot.command()
async def gif(ctx, input):
    # Specify parameters for request and send it
    params = {'api_key': GIPHY_API_KEY, 'q': input, 'rating': 'g', 'lang': "en"}
    response = requests.get(GIPHY_BASE_URL, params=params)

    # Check if the status code is good
    if response.status_code == 200:
        # Take the url from the dict
        data = response.json()['data']
        random_data = random.choice(data)
        gif_url = random_data['images']['original']['url']
        await ctx.send(gif_url)
    # If the status code is an error code, send an error message
    else: 
        await ctx.send("Error sending request. Try again later.")


# Implementing new API Waifu.im as a bot command
@bot.command()
async def waifu(ctx, input='waifu'):

    # Specify the parameters for the request
    params = {'included_tags': input, 'many': False}
    response = requests.get(WAIFU_BASE_URL, params=params)

    # Check if the status code is good
    if response.status_code == 200:
        # Take the url from the dict
        data = response.json()
        waifu_url = data['images'][0]['url']
        await ctx.send(waifu_url)
    # If the status code is an error code, send an error message
    else:
        await ctx.send("Error sending request. Try again later")


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
     
    elif "pls jojos" == user_message.lower():
        response = random.choice(JoJo_quotes)
        await message.channel.send(response)
        await gif(message.channel, "JoJos Anime")
  
    elif "pls inspire" == user_message.lower():
        response = random.choice(Vagabond_quotes)
        await message.channel.send(response)
        await gif(message.channel, "Rick Ross")

    elif "pls" in user_message:
        await message.channel.send("Not a valid command. Try using '!help'.")


    await bot.process_commands(message)

#**********************************************

# Audio commands

# Spotify API functions ---

# parse the video title into song name and artist name if possible
def spotify_info(ctx, video_title, input, url_or_search):

    print(f'"Debugging reasons": \n Video title: {video_title} \n')
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
        artist_name = 'Unknown' # The artist name is unkown since we only have song name
        song_name = video_title.split('(')[0] # Get the song name 
        song_info = spotify_search(song_name) # Send a request to Spotify API only with a track name
    # This means that the whole title is just the song so we set the artist name to unknown and assign the song name to the video title itself
    else:
        artist_name = 'Unknown'
        song_name = video_title
        song_info = spotify_search(song_name)

    # print statement to double check if the variables are as they should be
    print(f'"Debugging reasons": \n Song name: {song_name} \n Artist name: {artist_name} \n')

    # if song_info doesn't return Unknown it means that the request didn't have any problems
    if song_info[0] != 'Unknown':
        return (get_embed_msg(ctx, input, song_info, song_name, url_or_search))
    else:
        return (discord.Embed(colour= discord.Color.purple(), title='Unable to showcase additional information.')) 


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
def get_embed_msg(ctx, thumbnail_param, song_info, song_name, url_or_search):

    # Create embed object
    embed = discord.Embed(colour= discord.Color.orange(), title= f'Now playing: {song_name}!', description=f'Album name: {song_info[0]}')

    # Set footer
    embed.set_footer(text= f'Song requested by {ctx.message.author}.')

    # Set author 
    embed.set_author(name= bot.user, url= 'https://github.com/Feli05/DiscordBot')
    
    # Set other components
    embed.set_thumbnail(url= 'https://i.postimg.cc/pXWmBpGJ/discord-bot-profile.jpg')

    # if url_or_search returns True, it means the thumbnail_url is a url and we call the Youtube class, else we call the Search class
    if url_or_search:
        embed.set_image(url= YouTube(thumbnail_param).thumbnail_url)
    else:
        embed.set_image(url= Search(thumbnail_param).results[0].thumbnail_url)

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
async def play(ctx, *args):

    # Check if the user actually inputs something with the play command
    if not args:
        await ctx.send("You forgot to send a YT url or the name of the song!")
    else:
        input = ' '.join(args) # Concat the args list with spaces. This will prevent errors from when the user uses the search functionality

        # Rest of the play functionality
        try:
            voice_client = ctx.message.guild.voice_client
            if not voice_client:
                await ctx.send("Bot is not connected to a voice channel.")
                return

            async with ctx.typing():
                print('About to create player for music.')

                # Assign a Stream object to the yt variable to then reproduce and also assign boolean to variable Type so it knows its a url or text search
                # If the input is Youtube link then use the Youtube class
                if 'https://www.youtube.com' in input:
                    link = YouTube(input).streams.filter(only_audio=True).get_audio_only() 
                    yt = link
                    url_or_search = True
                # If the input is normal text, use the Search class
                else: 
                    search = Search(input).results[0].streams.filter(only_audio=True).get_audio_only()
                    yt = search
                    url_or_search = False

                print('Successfully created player!')

                # Stream the audio with options '-vn' which disable video so it focuses on audio only 
                voice_client.play(discord.FFmpegPCMAudio(yt.download(), options = '-vn'))
                # Send a message with information extracted from the Spotify metadata
                response = spotify_info(ctx, yt.title, input, url_or_search)
            
            # Send the embedded message
            await ctx.send(embed=response)

            # Wait for the music to stop playing
            while voice_client.is_playing() or voice_client.is_paused():
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