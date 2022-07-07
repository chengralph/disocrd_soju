import discord
from discord.ext import commands

from app.aws import dynamodb
from app.common.log import get_logger
from app.lichess.lichess import LiChess

log = get_logger()
lichess = LiChess()


class Init(commands.Cog):
    @commands.command()
    async def token(self, message, content):
        if isinstance(message.channel, discord.channel.DMChannel) and message.author.name != 'Soju🍾':
            log.info(f'{message.author.name} DMed Soju🍾')
            log.info(content)
            lichess_username = await lichess.auth(content)
            if lichess_username:
                players = dynamodb.get_items("player")
                player = [player if player["discord_id"] == message.author.id else {} for player in players][0]
                if player:
                    log.info(f'Player exists {player}')
                    player["token"] = message.content
                    dynamodb.update_item("player", player)
                    await self.send_dm(message, "LiChess Token has been updated.")
                else:
                    item = {
                        "lichess": lichess_username,
                        "discord_id": message.author.id,
                        "handicap": False,
                        "token": message.content,
                        "discord": message.author.name
                    }
                    log.info(f'Player does not exist: {player}')
                    dynamodb.put_item("player", item)
                    await self.send_dm(message, "LiChess Token has been stored.")
            else:
                await self.send_dm(message, "Please send correct LiChess API")

    @commands.command()
    async def init(self, message):
        log.info(f'{message.author.name} used init')
        await message.channel.send(f'DM sent {message.author}')
        await self.send_dm(message, "Please create LiChess API will full access: "
                                    "https://lichess.org/account/oauth/token. "
                                    "\nPlease reply with your API Token with the $token command. "
                                    "\nExample: ```$token lip_1234567890```")

    @staticmethod
    async def send_dm(message, content):
        try:
            await message.author.send(content)
        except (Exception,) as e:
            log.error(e)


def setup(bot):
    bot.add_cog(Init(bot))
