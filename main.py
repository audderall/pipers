import logging
import os
from datetime import datetime

import discord
from dotenv import load_dotenv

from core.bump import bump

logging.disable(logging.INFO)


load_dotenv()
TOKEN = os.getenv("USER_TOKEN")
DISBOARD_APP_ID = "302050872383242240"
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

client = discord.Client()

print("logging in...")


@client.event
async def on_ready():
    print(f"logged in as {client.user} at {now()}")
    try:
        channel_id = await bump(client, CHANNEL_ID, DISBOARD_APP_ID)
        print(f"bumped successfully in channel {channel_id} at {now()}")
    except Exception as e:
        print(e)
    finally:
        await client.close()


def now():
    return datetime.now().replace(microsecond=0)


client.run(TOKEN)
