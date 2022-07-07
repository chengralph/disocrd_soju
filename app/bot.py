import discord
import json

from app.lichess.lichess import LiChess
from app.common.common import modelize
from app.common.log import get_logger
from app.aws import dynamodb

log = get_logger()


class MyClient(discord.Client):
    lichess = LiChess()

    async def on_ready(self):
        log.info(f'Logged on as {self.user}')

    async def on_message(self, message):
        log.info(f'Message in chat: {message}')
        if message.content.startswith('$init'):
            log.info(f'{message.author.name} used init')
            await message.channel.send(f'DM sent {message.author}')
            await self.send_dm(message, "Please create LiChess API will full access: "
                                        "https://lichess.org/account/oauth/token."
                                        "Please reply with your API Token.")

        if isinstance(message.channel, discord.channel.DMChannel) and message.author.name != 'Soju🍾':
            log.info(f'{message.author.name} DMed Soju🍾')
            lichess_username = await self.lichess.auth(message.content)
            if lichess_username:
                items = dynamodb.get_items("player")
                item = [item if item["discord_id"] == message.author.id else {} for item in items][0]
                if item:
                    log.info(f'Player exists {item}')
                    item["token"] = message.content
                    dynamodb.update_item("player", item)
                    await self.send_dm(message, "LiChess Token has been updated.")
                else:
                    item = {
                        "lichess": lichess_username,
                        "discord_id": message.author.id,
                        "handicap": False,
                        "token": message.content,
                        "discord": message.author.name
                    }
                    log.info(f'Player does not exist {item}')
                    dynamodb.put_item("player", item)
                    await self.send_dm(message, "LiChess Token has been stored.")
            else:
                await self.send_dm(message, "Please send correct LiChess API")

        if message.content.startswith('$game'):
            with open("tokens.json", "r") as json_file:
                data = json.load(json_file)
                if str(message.author.id) in data:
                    p1, p2 = modelize(data[str(message.author.id)], data[message.content.split(" ")[1][2:-1]])
                    print(p1, p2)
                    try:
                        if p1.handicap or p2.handicap:
                            base_time, handicap_time = await self.lichess.time_calculation(p1, p2)
                            game_link, game_id = await self.lichess.challenge(p1.token, p2.lichess, base_time)
                            await message.channel.send(f'Link: <{game_link}>')
                            # Need to add logic for non-handicapped person to add time, p1.token or p2.token
                            if p2.handicap:
                                await self.lichess.time_appropriation(p1.token, game_id, handicap_time)
                            elif p1.handicap:
                                await self.lichess.time_appropriation(p2.token, game_id, handicap_time)
                            await self.lichess.get_result(game_id)
                        else:
                            game_link, game_id = await self.lichess.challenge(p1.token, p2.lichess, 300)
                            await message.channel.send(f'Link: <{game_link}>')
                            await self.lichess.get_result(game_id)
                    except Exception as err:
                        print(err)
                        await message.channel.send(f'ERROR')
                else:
                    await message.channel.send(f'{message.author} not authenticated. To authenticate do $init')

        if message.content.startswith('$result'):
            with open("tokens.json", "r") as json_file:
                data = json.load(json_file)
                if str(message.author.id) in data:
                    print("User Authenticated")
                    try:
                        challenged_user_id = message.content.split(" ")[1][2:-1]
                        challenged_user_name = data.get(challenged_user_id)["lichess"]

                        await self.lichess.get_result(challenged_user_name)
                    except Exception as err:
                        print(err)
                        await message.channel.send(f'ERROR')
                else:
                    await message.channel.send(f'{message.author} not authenticated. To authenticate do $init')


    @staticmethod
    async def send_dm(message, content):
        try:
            await message.author.send(content)
        except (Exception,):
            pass
