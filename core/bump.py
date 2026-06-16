import asyncio
from datetime import datetime

async def bump(bot, channel_id, application_id):
    channel = bot.get_channel(int(channel_id))
    if channel is None:
        print(f"channel {channel_id} is not found")
        return False
    try:
        command_list = await channel.application_commands()
        for cmd in command_list:
            if cmd.application_id == int(application_id):
                await cmd()
                print(f"bumped {channel_id} at {datetime.now()}")
                return True
        print("error")
        return False
    except Exception as e:
        print(f"exception {e}")
        return False
