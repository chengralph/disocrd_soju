import discord
import json
import logging

from app.lichess import LiChess
from app.misc import modelize


class MyClient(discord.Client):
    lichess = LiChess()

    async def on_ready(self):
        print(f'Logged on as {self.user}')
        logging.debug(f'Logged on as {self.user}')

    async def on_message(self, message):
        print(f'Message in chat: {message}')
        if message.content.startswith('$init'):
            await message.channel.send(f'DM sent {message.author}')
            await self.send_dm(message, "Please create LiChess API will full access: "
                                        "https://lichess.org/account/oauth/token."
                                        "Please reply with your API Token.")

        if isinstance(message.channel, discord.channel.DMChannel) and message.author.name != 'Soju🍾':
            logging.debug(f"---Message from Sender: {message.author.name}---")
            lichess_id = await self.lichess.auth(message.content)
            if lichess_id:
                with open("tokens.json", "r+") as json_file:
                    data = json.load(json_file)
                    if str(message.author.id) in data:
                        data[str(message.author.id)]["token"] = message.content
                        await self.send_dm(message, "LiChess Token has been updated.")
                    else:
                        data_obj = {
                            message.author.id: {
                                "lichess": lichess_id,
                                "discord": message.author.name,
                                "token": message.content
                            }
                        }
                        data.update(data_obj)
                        json_file.seek(0)
                        json.dump(data, json_file, indent=4)
                        json_file.truncate()
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
                            await self.lichess.time_appropriation(p1.token, game_id, handicap_time)
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

                        await self.lichess.get_result(message, challenged_user_name)
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
