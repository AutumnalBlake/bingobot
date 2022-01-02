import discord
import os

intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print (f"{message.author}: {message.content}")
    print (message.channel.members)

    if message.content.startswith('!bingo'):
        ch = message.channel
        ch_memb_ids = [m.id for m in ch.members]
        tags = message.mentions
        if len(tags) != 1:
            await message.channel.send(f"<@{message.author.id}> usage: `!bingo <@user>` to start a game with another player")
            return
        p2 = tags[0].id
        if p2 not in ch_memb_ids:
            await message.channel.send(f"<@{message.author.id}> second player must be a member of this channel!")
            return
        await message.channel.send(f"<@{message.author.id}> successful")
        
        



# Just for fun
# @client.event
# async def on_typing(channel, user, when):
#     await channel.send(f"<@{user.id}> stop typing")


client.run(os.getenv('BINGOTOKEN'))
