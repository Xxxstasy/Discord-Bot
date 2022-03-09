import logging
import discord
from discord.ext import commands
from config import settings
import youtube_dl
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
import requests
from replit import db
from datetime import datetime, timedelta
import aiohttp

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=settings['prefix'], intents=intents)
queue = []
past = datetime(2009, 12, 2, 9, 30)
client = discord.Client()


@bot.command()
async def hello(ctx):
    author = ctx.message.author

    await ctx.send(f'Ку, {author.mention}!')


@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


@bot.command()
async def play(ctx, url):
    ydl_options = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        with YoutubeDL(ydl_options) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['url']
        voice.play(discord.FFmpegPCMAudio(executable="F:\FFmpeg\\ffmpeg.exe", source=URL, **FFMPEG_OPTIONS))
        voice.is_playing()
        await ctx.send('Now playing' + info.get('title'))


@bot.command()
async def serverQueue(voice, message):
    if queue != [] and not voice.is_playing():
        await play(queue.pop(0), voice, message)
        print('queue - ' + str(queue))


@bot.command()
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Currently no song is playing.")


@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The song is not paused.")


@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()


@bot.command()
async def skip(ctx, message, info):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()
    await serverQueue(voice, message)
    await ctx.message.channel.send('Successfully skipped - ' + message)


@bot.command()
async def hug(ctx):
    async with aiohttp.ClientSession() as session:
        request = await session.get('https://some-random-api.ml/animu/hug')
        hug_json = await request.json()
    embed = discord.Embed(color=discord.Color.dark_orange())
    embed.set_image(url=hug_json['link'])
    await ctx.message.channel.send(embed=embed)


@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, id=942700385762701332)
    await member.add_roles(role)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('Dota 2 на течисе'))


def get_prices(crypto):
    global past
    URL = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd'
    now = datetime.now() - timedelta(minutes=1)
    if now > past:
        result = requests.get(url=URL)
        data = result.json()
        bot.request_cache = data
        past = datetime.now()
    for i in range(len(bot.request_cache)):
        if bot.request_cache[i]['id'] == crypto:
            return bot.request_cache[i]['current_price']


@bot.event
async def on_message(message):
    global past
    if message.author == client.user:
        return
    x = get_prices(message.content.lower())
    if x:
        await message.channel.send(f'The сurrent price of {message.content} is {x} USD')
    await bot.process_commands(message)


bot.run(settings['token'])
