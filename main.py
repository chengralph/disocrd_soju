import discord
import os
import requests
import json
import asyncio
from lichess_client import APIClient
from lichess_client.utils.enums import StatusTypes
DISCORD_TOKEN = "ODkxNDk5MjMzNjc5NjU5MTA5.YU_PXA.mUiKAwVX4ekR_VAhrEfjeXJe9Xw"
MY_LICHESS_TOKEN = "lip_bdTUcHlMEnaAgPILaexV"


class LiChess:
    def __init__(self):
        self.lichess_client = None

    async def auth(self, lichess_token):
        """
        # INSERT CODE HERE
        response = await self.lichess_client {WHAT FUNCTION GOES HERE TO VALIDATE} https://github.com/amasend/lichess_python_SDK/tree/master/lichess_client/endpoints
        # Okay now you have a response object, print it out. How do we tell if its GOOD OR BAD?
        # We want a condition for if the response is GOOD.
        # What you need to do. Pass in good token, see the object, Pass in bad token, see the object, what differs?
        if response GOOD:
            return True
        else:
            return False
        """

        pass

    async def challenge(self):
        response = await self.lichess_client.challenges.create("ZetaPulse")
        print(response)


class MyClient(discord.Client):
    lichess = LiChess()

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if message.content.startswith('$init'):
            await message.channel.send(f'DM sent {message.author}')
            await self.send_dm(message, "Please enter your LiChess API: https://lichess.org/account/oauth/token")

        if isinstance(message.channel, discord.channel.DMChannel) and message.author.name !='Soju🍾':
            if message.content:
                response = await self.lichess.auth()
                # if response.entity.status == StatusTypes.ERROR:
                #     await self.send_dm(message, "Please send correct Lichess API")
                # else:
                #     await self.send_dm(message, "Thanks :)")
                    # with open("tokens.json", "w+") as f:
                    #     data = json.load(f)
                    #     print(data)
                    #     data.update({message.author: message.content})
                    #     print(data)
                    #     json.dump(data, f)

        print(f'Message from {message.author} [{message.author.id}]: {message.content}')

    async def send_dm(self, message, content):
        try:
            await message.author.send(content)
        except (Exception,):
            pass





#
# get_or_create_loop().run_until_complete(account())
# asyncio.run(challenge())
# asyncio.run(challenge()) # loop is null, create new
# print(asyncio.get_event_loop().is_closed())
# print("hi")

client = MyClient()
client.run(DISCORD_TOKEN)

