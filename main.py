import discord
import requests
import json
from lichess_client import APIClient
from lichess_client.utils.enums import StatusTypes
DISCORD_TOKEN = "ODkxNDk5MjMzNjc5NjU5MTA5.YU_PXA.mUiKAwVX4ekR_VAhrEfjeXJe9Xw"
MY_LICHESS_TOKEN = "lip_bdTUcHlMEnaAgPILaexV"
CHALLANGEE = "sleepylunatic"

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
        if response.entity.status == StatusTypes.SUCCESS:
            self.content_challange = response.entity.content["challenge"]
            return self.content_challange["url"], self.content_challange["id"]
        raise Exception

    async def time_calculation(self, lichess_token):
        lichess_id = await self.auth(lichess_token)
        with open("scores.json", "r+") as json_file:
            data = json.load(json_file)
            if lichess_id in data:
                losses = data[lichess_id][CHALLANGEE]
                set_time = 120 + (losses * 15)
                opponent_time = (12 * 60) - (losses * 15) - set_time
                return set_time, opponent_time
            else:
                data_obj = {
                    lichess_id: {
                        "sleepylunatic": 0,
                    }
                }
                data.update(data_obj)
                json_file.seek(0)
                json.dump(data, json_file, indent=4)
                json_file.truncate()
                return 120, 600

    async def time_appropriation(self, lichess_token, game_id, seconds):
        headers = {
            'Authorization': f'Bearer {lichess_token}',
            'Content-Type': 'application/json'
        }

        while True:
            response = requests.post(url=f"https://lichess.org/api/round/{game_id}/add-time/{seconds}",
                                     headers=headers)
            if response.ok:
                print(f"Time Added: {response}")
                break

    async def get_result(self, lichess_token, game_id):
        lichess_id = await self.auth(lichess_token)
        "while True:"
        response = await self.lichess_client.games.export_one_game(game_id)
        """
        if response["status"]:
            if response["status"] == "win" and response["players"] == "zetapulse":
                data = json.load(json_file)
                data_obj[lichess_id]["zetapulse"] += 1 
                json_file.seek(0)
                json.dump(data, json_file, indent=4)
                json_file.truncate()
                break
        """


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
            lichess_id = await self.lichess.auth(message.content)
            if lichess_id:
                with open("tokens.json", "r+") as json_file:
                    data = json.load(json_file)
                    if str(message.author.id) in data:
                        await self.send_dm(message, "Your Lichess Token is already recorded")
                    else:
                        data_obj = {
                            message.author.id: {
                                "lichess": lichess_id,
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
                    try:
                        set_time, opponent_time = await self.lichess.time_calculation(lichess_token)
                        challenge_link, challenge_id = await self.lichess.challenge(lichess_token, CHALLANGEE, set_time)
                        await message.channel.send(f'Link: <{challenge_link}>')
                        await self.lichess.time_appropriation(lichess_token, challenge_id, opponent_time)
                        await self.lichess.get_result(lichess_token, challenge_id)
                    except:
                        await message.channel.send(f'ERROR')
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

