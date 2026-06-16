async def bump(bot, channel_id, application_id):
    channel = bot.get_channel(int(channel_id))
    if channel is None:
        raise ValueError(f"channel {channel_id} not found")

    command_list = await channel.application_commands()
    for cmd in command_list:
        if cmd.application_id == int(application_id):
            await cmd()
            return channel_id
        return False
    raise ValueError(f"application {application_id} not found in channel {channel_id}")
