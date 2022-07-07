from discord.ext import commands

from app.aws import dynamodb
from app.common.log import get_logger
from app.lichess.lichess import LiChess
from app.models.models import Player

log = get_logger()
lichess = LiChess()


class Game(commands.Cog):
    @commands.command()
    async def game(self, message, content):
        log.info(f'{message.author.name} used game')
        players = dynamodb.get_items("players")
        player1 = [player if player["discord_id"] == message.author.id else {} for player in players][0]
        player2 = [player if player["discord_id"] == content[2:-1] else {} for player in players][0]
        log.info(f'Player 1: {player1}')
        log.info(f'Player 1: {player2}')
        p1 = Player(**player1)
        p2 = Player(**player2)
        try:
            if p1.handicap or p2.handicap:
                base_time, handicap_time = await lichess.time_calculation(p1, p2)
                game_link, game_id = await lichess.challenge(p1.token, p2.lichess, base_time)
                await message.channel.send(f'Link: <{game_link}>')
                # Need to add logic for non-handicapped person to add time, p1.token or p2.token
                if p2.handicap:
                    await lichess.time_appropriation(p1.token, game_id, handicap_time)
                elif p1.handicap:
                    await lichess.time_appropriation(p2.token, game_id, handicap_time)
                await lichess.get_result(game_id)
            else:
                game_link, game_id = await lichess.challenge(p1.token, p2.lichess, 300)
                await message.channel.send(f'Link: <{game_link}>')
                await lichess.get_result(game_id)
        except Exception as err:
            print(err)
            await message.channel.send(f'ERROR')



def setup(bot):
    bot.add_cog(Game(bot))
