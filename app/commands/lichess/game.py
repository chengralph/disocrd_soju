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
    async def game(self, message, content):
        log.info(f'{message.author.name} used game')
        players = dynamodb.get_items("players")
        print(content[2:-1])
        print(type(content[2:-1]))
        print(players)
        player1 = [player for player in players if player["discord_id"] == str(message.author.id) ][0]
        player2 = [player for player in players if player["discord_id"] == str(content[2:-1])][0]
        log.info(f'Player 1: {player1}')
        log.info(f'Player 2: {player2}')
        if not player1:
            await message.channel.send("Player 1 is not authenticated. Please use $init.")
        if not player2:
            await message.channel.send("Player 2 is not authenticated. Please use $init.")
        p1 = Player(**player1)
        p2 = Player(**player2)
        try:
            log.info(f"P1 Handicap: {p1.handicap}\n P2 Handicap {p2.handicap}")
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
        """
        Starts Handicap Match
        @param game_id:
        @param handicap_player:
        @param stronger_player:
        @return:
        """
        log.info("Start Handicap Time")
        handicap_bonus_time, stronger_bonus_time = await lichess.calculate_bonus_time(handicap_player, stronger_player)
        log.info(f"Handicap Bonus Time: {handicap_bonus_time}, Stronger Bonus Time {stronger_bonus_time}")
        tasks = [lichess.appropriate_time(handicap_player.token, game_id, stronger_bonus_time),
                 lichess.appropriate_time(stronger_player.token, game_id, handicap_bonus_time)]
        results = await asyncio.gather(*tasks)
        log.info(results)
        log.info(f"Time Added for {stronger_player}")
        log.info(f"Time Added for {handicap_player}")
        await lichess.get_result(game_id)


def setup(bot):
    bot.add_cog(Game(bot))
