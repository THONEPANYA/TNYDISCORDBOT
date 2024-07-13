import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import os

# ใช้โทเคนที่ให้มา
TOKEN = 'MTA5NDc4MDIxOTkwMDA0MzM2NQ.GbCtX9.3xkRpI9gKDFlklSlGUWWgrT7KKaeYCtGmymQqc'

# ตั้งค่าตำแหน่งของ ffmpeg
ffmpeg_path = "C:\\PATH_Programs\\ffmpeg.exe"
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

# ตรวจสอบการนำเข้า PyNaCl
try:
    import nacl
    print('PyNaCl is installed and imported')
except ImportError:
    print('PyNaCl is not installed or cannot be imported')

# กำหนด intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# สร้างอินสแตนซ์บอทด้วยคำสั่ง prefix '!'
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

@bot.command(name='play')
async def play(ctx, url: str):
    # ตรวจสอบว่าผู้ใช้เชื่อมต่อกับช่องเสียงหรือไม่
    if not ctx.author.voice:
        await ctx.send("คุณยังไม่ได้เชื่อมต่อกับช่องเสียง")
        return

    channel = ctx.author.voice.channel

    # เชื่อมต่อกับช่องเสียง
    if not ctx.voice_client:
        await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)

    # ตั้งค่า yt_dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            print(f'Download URL: {url2}')  # เพิ่มบรรทัดนี้เพื่อตรวจสอบ URL

            # ลองเล่น URL ด้วย ffmpeg โดยตรง
            ffmpeg_test_command = f'ffmpeg -i "{url2}" -f null -'
            os.system(ffmpeg_test_command)

            # เล่นเสียง
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
                'options': '-vn'
            }
            source = discord.FFmpegPCMAudio(url2, **ffmpeg_options)
            ctx.voice_client.play(source, after=lambda e: print(f'Error: {e}') if e else None)
            await ctx.send(f'กำลังเล่น: {info["title"]}')
    except Exception as e:
        await ctx.send(f'เกิดข้อผิดพลาด: {str(e)}')

    # ดีบักเพิ่มเติม
    print(f"Voice client connected: {ctx.voice_client.is_connected()}")
    print(f"Voice client playing: {ctx.voice_client.is_playing()}")

@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f'ลบข้อความ {len(deleted)} ข้อความเรียบร้อยแล้ว', delete_after=5)

@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user and after.channel is None:
        print("Bot was disconnected from the voice channel")
        await bot.voice_clients[0].disconnect()

# รันบอท
bot.run(TOKEN)
