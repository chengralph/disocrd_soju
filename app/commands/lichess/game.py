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
            if p1.handicap and p2.handicap:
                game_link, game_id = await lichess.challenge(p1.token, p2.lichess, 600)
                await message.channel.send(f'Link: <{game_link}>')
                await lichess.get_result(game_id)
            elif p1.handicap:
                game_link, game_id = await lichess.challenge(p1.token, p2.lichess, 120)
                await message.channel.send(f'Link: <{game_link}>')
                await self.handicap_start(game_id=game_id, handicap_player=p1, stronger_player=p2)
            elif p2.handicap:
                game_link, game_id = await lichess.challenge(p1.token, p2.lichess, 120)
                await message.channel.send(f'Link: <{game_link}>')
                await self.handicap_start(game_id=game_id, handicap_player=p2, stronger_player=p1)
            else:
                game_link, game_id = await lichess.challenge(p1.token, p2.lichess, 300)
                await message.channel.send(f'Link: <{game_link}>')
                await lichess.get_result(game_id)
        except Exception as err:
            log.error(err)
            await message.channel.send(err)

    async def handicap_start(self, game_id: str, handicap_player: Player, stronger_player: Player):
        handicap_bonus_time, stronger_bonus_time = await lichess.calculate_bonus_time(handicap_player, stronger_player)
        await lichess.approriate_time(handicap_player.token, game_id, stronger_bonus_time)
        log.info(f"Time Added for {stronger_player}")
        await lichess.approriate_time(stronger_player.token, game_id, handicap_bonus_time)
        log.info(f"Time Added for {handicap_player}")
        await lichess.get_result(game_id)


def setup(bot):
    bot.add_cog(Game(bot))
