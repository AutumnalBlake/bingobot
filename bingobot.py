import discord
import os
from bingogame import BingoGame
import asyncio

INVITE_EXPIRY = 60
BINGO_DELAY = 15
DRAW_DELAY = 7

intents = discord.Intents.all()
client = discord.Client(intents=intents)

active_invites = {} # channel : (user, invitee or none, game_opts(,))
active_games = {}   # channel : (user1, user2, BingoGame instance)

enabled_channels = []

async def enable(channel):
    if channel in enabled_channels:
        enabled_channels.remove(channel)
        await channel.send(f"Bingobot disabled in #{channel.name}.")
    else:
        enabled_channels.append(channel)
        await channel.send(f"Bingobot enabled in #{channel.name}.")

async def start_game(channel, player1, player2, size = 5, fs = True):
    global active_games

    game = BingoGame(player1.name, player2.name, size, fs)
    active_games[channel] = (player1, player2, game)

    await channel.send("When you have a bingo, type `BINGO` in the chat.")
    await channel.send(f"```\n{str(game)}\n```")

    drawn_message = await channel.send("Drawn numbers: ")

    while not game.is_finished:
        try:
            num = game.draw()
        except:
            await channel.send("Ran out of numbers, game over.")
            game.end()
            active_games.pop(channel)
        
        msg = f"{drawn_message.content}  **{num}**" 
        await asyncio.sleep(DRAW_DELAY)
        await drawn_message.edit(content=msg)


async def bingo_call(channel, player):
    global active_games

    if channel not in active_games.keys():
        await channel.send("There is no bingo game active in this channel!")
        return

    if player not in active_games[channel]:
        await channel.send("You are not participating in this game.")
        return

    game = active_games[channel][2]
    p_idx = active_games[channel].index(player)

    if game.has_bingo(p_idx):
        active_games.pop(channel)
        game.end()
        await channel.send(f"BINGO! {player.name} wins!")
    
    else:
        await channel.send(f"You don't have a bingo yet!")

async def show_help(channel):
    await channel.send(f"""```
!bingo enable         toggle whether bingobot is enabled here (disabled by default)
!bingo help:          display this message
!bingo @user:         invite a user to play bingo, if no user is specified anyone can accept
    Optional args -
    size=3/5/7:       choose a board size
    fs=on/off         free space toggle
    
!bingo accept:        accept an invitation to play bingo
!bingo credits:       read additional information about this bot
```""")

async def show_credits(channel):
    await channel.send(f"""
This bot was programmed by Blake Morris, using the discord.py library by Rapptz.

Source code: https://github.com/AutumnalBlake/bingobot

discord.py license information:
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
""")

async def create_invite(channel, user, invitee, game_opts = ()):
    global active_invites
    
    if channel in active_invites:
        await channel.send("There is already an active invite in this channel, please wait for it to expire.")
        return
    
    if channel in active_games:
        await channel.send("There is already an active game in this channel, please wait for it to end.")
        return
    
    active_invites[channel] = (user, invitee, game_opts)
    await channel.send(f"Invite created, accept with `!bingo accept`. Will expire in {INVITE_EXPIRY} seconds.")
    
    # Schedule expiry
    client.loop.call_later(INVITE_EXPIRY, active_invites.pop, channel)
    

async def accept_invite(channel, user):
    global active_invites

    if channel not in active_invites:
        await channel.send("There is no active invite in this channel!")

    elif active_invites[channel][1] in (user, None):
        await channel.send("Invite accepted, game starting...")
        await start_game(channel, active_invites[channel][0], user, *active_invites[channel][2])
        active_invites.pop(channel)

    else:
        await channel.send("You haven't been invited to a game in this channel, please wait for the current game to end.")


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!bingo'):
        print (f"{message.author}: {message.content}")
        args = message.content.split()[1:]
        
        if args[0] == "help" or len(args) == 0:
            await show_help(message.channel)
        
        elif args[0] == "enable":
            if message.author.permissions_in(message.channel).manage_channels:
                await enable(message.channel)
            else:
                await message.channel.send("You must have manage channels permissions to do this")

        elif message.channel in enabled_channels:
            if args[0] == "credits":
                await show_credits(message.channel)

            elif args[0] == "accept":
                await accept_invite(message.channel, message.author)

            elif len(message.mentions) == 1:
                fs = False if 'fs=off' in message.content else True
                size = 5
                if 'size=3' in message.content:
                    size = 3
                if 'size=7' in message.content:
                    size = 7
                await create_invite(message.channel, message.author, message.mentions[0], (size, fs))

    if not message.content.startswith('!') and 'BINGO' in message.content.upper() and message.channel in active_games.keys():
        await bingo_call(message.channel, message.author)


if __name__ == "__main__":
    client.run(os.getenv('BINGOTOKEN'))




