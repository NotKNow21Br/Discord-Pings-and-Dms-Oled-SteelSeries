import discord
from discord.ext import commands
from easyhid import Enumeration
from time import sleep
from signal import signal, SIGINT, SIGTERM
from sys import exit
from playsound import playsound
from PIL import Image, ImageDraw, ImageFont
import asyncio


TOKEN = ""


resolution = (128, 40)

supported_pid = (5650, 5656, 5648, 5660)


glass = commands.Bot(command_prefix="!", help_command=None, self_bot=True, case_insensitive=True)
bot_init = False


def getdevice():
    en = Enumeration()
    devices = en.find(vid=0x1038, interface=1)
    for device in devices:
        if device.product_id in supported_pid:
            print(f"Found device: {device.product_string}")
            return device
    exit("No compatible SteelSeries devices found, exiting.")


def signal_handler(sig, frame):
    try:
        dev.send_feature_report(bytearray([0x61] + [0x00] * 641))  # Clear the screen
        dev.close()
        print("\n")
        exit(0)
    except Exception as e:
        exit(str(e))

signal(SIGINT, signal_handler)
signal(SIGTERM, signal_handler)

dev = getdevice()
dev.open()

async def display_message_on_keyboard(text):
    img = Image.new('1', resolution, 0)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()  # Adjust font as needed
    draw.text((0, 0), text, fill=255, font=font)
    
    data = img.tobytes()
    frame_data = bytearray([0x61]) + data + bytearray([0x00])
    dev.send_feature_report(frame_data)

    await asyncio.sleep(10)
    
    dev.send_feature_report(bytearray([0x61] + [0x00] * 641))  # Clear the screen

@glass.event
async def on_ready():
    global bot_init
    bot_init = True
    print(f'Logged in as {glass.user}')

@glass.event
async def on_message(message):
    if message.author == glass.user:
        return  

    if glass.user in message.mentions:
        print(f"Ping from {message.author}: {message.content}")
        await display_message_on_keyboard(f"Ping: {message.author.name}")
        playsound('ping_notification.mp3')  # Play sound

    elif isinstance(message.channel, discord.DMChannel):
        print(f"DM from {message.author}: {message.content}")
        await display_message_on_keyboard(f"DM: {message.author.name}")
        playsound('dm_notification.mp3')  # Different sound for DMs

glass.run(TOKEN, bot=False, reconnect=True)