import discord
from discord.ext import commands

from app.aws import dynamodb
from app.common.log import get_logger
from app.lichess.lichess import LiChess


log = get_logger("standard")
lichess = LiChess()


class Init(commands.Cog):
    @commands.command()
    async def handicap(self, message, content):
        """
        Handicap Command to set handicap to true/false
        @param message:
        @param content:
        @return:
        """
        log.info(f'{message.author.name} used handicap')
        log.info(content)
        item = {
            "discord_id": str(message.author.id),
            "discord": message.author.name
        }
        player = dynamodb.get_item(item, "players")
        try:
            handicap = bool(int(content))
            if player:
                log.info(f'Player exists {player}')
                dynamodb.update_item(item, "handicap", handicap, "players")
                await message.channel.send(f"{message.author.name}'s handicap has been set to: {handicap}")
            else:
                await message.channel.send("Please use $init to set up your user.")
        except Exception as err:
            log.error(err)
            message.channel.send("Please use 0=False or 1=True.")

    @commands.command()
    async def token(self, message, content):
        """
        Token command to set content of lichess token in Players DynamoDB
        @param message:
        @param content:
        @return:
        """
        if isinstance(message.channel, discord.channel.DMChannel) and message.author.name != 'Soju🍾':
            log.info(f'{message.author.name} DMed Soju🍾')
            log.info(content)
            lichess_username = await lichess.auth(content)
            if lichess_username:
                item = {
                    "discord_id": str(message.author.id),
                    "discord": message.author.name
                }
                player = dynamodb.get_item(item, "players")
                if player:
                    log.info(f'Player exists {player}')
                    dynamodb.update_item(item, "token", str(content), "players")
                    await self.send_dm(message, "LiChess Token has been updated.")
                else:
                    log.info(f'Player does not exist: {player}')
                    item = {
                        "lichess": lichess_username,
                        "discord_id": str(message.author.id),
                        "handicap": False,
                        "token": content,
                        "discord": message.author.name
                    }
                    dynamodb.put_item("players", item)
                    await self.send_dm(message, "LiChess Token has been stored.")
            else:
                await self.send_dm(message, "Please send correct LiChess API")

    @commands.command()
    async def init(self, message):
        """
        Init Command instruct player to use token command
        @param message:
        @return:
        """
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
