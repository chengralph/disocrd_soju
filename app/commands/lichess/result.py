from discord.ext import commands
import asyncio

from app.aws import dynamodb
from app.common.log import get_logger
from app.lichess.lichess import LiChess
from app.models.models import Player

log = get_logger("standard")
lichess = LiChess()


class Game(commands.Cog):
    @commands.command()
    async def result(self, message, content):
        log.info(f'{message.author.name} used game')
        players = dynamodb.get_items("players")
        player1 = [player for player in players if player["discord"] == "Arlo"][0]
        player2 = [player for player in players if player["discord"] == "Ralph"][0]
        log.info(f'Player 1: {player1}')
        log.info(f'Player 2: {player2}')
        await lichess.get_result(content, player1, player2)



def setup(bot):
    bot.add_cog(Game(bot))
