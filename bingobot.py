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

    await message.channel.send(message.content)

# Just for fun
# @client.event
# async def on_typing(channel, user, when):
#     await channel.send(f"<@{user.id}> stop typing")


client.run(os.getenv('BINGOTOKEN'))
