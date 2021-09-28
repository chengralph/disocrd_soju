import discord
import os
import requests
import json
import asyncio
import time
from lichess_client import APIClient
from lichess_client.utils.enums import StatusTypes, RequestMethods
DISCORD_TOKEN = "ODkxNDk5MjMzNjc5NjU5MTA5.YU_PXA.mUiKAwVX4ekR_VAhrEfjeXJe9Xw"
MY_LICHESS_TOKEN = "lip_bdTUcHlMEnaAgPILaexV"


class LiChess:
    def __init__(self):
        self.lichess_client = None

    async def auth(self, lichess_token):
        self.lichess_client = APIClient(token=lichess_token)
        response = await self.lichess_client.account.get_my_profile()
        if response.entity.status == StatusTypes.SUCCESS:
            return response.entity.content['id']
        else:
            return False

    async def challenge(self, lichess_token, username: str, time_limit: int):
        await self.auth(lichess_token)
        response = await self.lichess_client.challenges.create(username=username, time_limit=time_limit, time_increment=0)
        print(response)
        return response.entity.content["challenge"]["url"], response.entity.content["challenge"]["id"]

    async def time_appropriation(self, lichess_token, game_id, time):
        await self.auth(lichess_token)
        self.lichess_client = APIClient(token=lichess_token)

        async def add_time(slf):
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = await slf._client.request(method=RequestMethods.POST,
                                                  url=f'api/round/{game_id}/add-time/{time}',
                                                  headers=headers)
            print(response)

        self.lichess_client.challenges.new_method = add_time
        await self.lichess_client.challenges.new_method(self.lichess_client.challenges)


class MyClient(discord.Client):
    lichess = LiChess()

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if message.content.startswith('$init'):
            await message.channel.send(f'DM sent {message.author}')
            await self.send_dm(message, "Please enter your LiChess API: https://lichess.org/account/oauth/token")

        if isinstance(message.channel, discord.channel.DMChannel) and message.author.name != 'Soju🍾':
            print(f"---Message from Sender: {message.author.name}---")
            response = await self.lichess.auth(message.content)
            if response:
                with open("tokens.json", "r+") as json_file:
                    data = json.load(json_file)
                    if str(message.author.id) in data:
                        await self.send_dm(message, "Your Lichess Token is already recorded")
                    else:
                        data_obj = {
                            message.author.id: {
                                "lichess": response,
                                "name": message.author.name,
                                "token": message.content
                            }
                        }
                        data.update(data_obj)
                        json_file.seek(0)
                        json.dump(data, json_file, indent=4)
                        json_file.truncate()
                        await self.send_dm(message, "Thanks :)")
            else:
                await self.send_dm(message, "Please send correct Lichess API")

        if message.content.startswith('$game'):
            with open("tokens.json", "r") as json_file:
                data = json.load(json_file)
                if str(message.author.id) in data:
                    print("User Authenticated")
                    lichess_token = data[str(message.author.id)]["token"]
                    challenge_link, challenge_id = await self.lichess.challenge(lichess_token, "zetapulse", 120)
                    await message.channel.send(f'Link: <{challenge_link}>')
                    time.sleep(10)
                    await self.lichess.time_appropriation(lichess_token, challenge_id, 120)
                else:
                    await message.channel.send(f'{message.author} not authenticated. To authenticate do $init')

        print(f'Message from {message.author} [{message.author.id}]: {message.content}')

    async def send_dm(self, message, content):
        try:
            await message.author.send(content)
        except (Exception,):
            pass


client = MyClient()
client.run(DISCORD_TOKEN)

