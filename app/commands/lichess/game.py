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
            log.info(f"P1 Handicap: {p1.handicap} || P2 Handicap {p2.handicap}")
            if p1.handicap and p2.handicap:
                game_link, game_id = await lichess.challenge(p1.token, p2.lichess, 600)
                await message.channel.send(f'Link: <{game_link}>')
                winning_player = await self.decide_winner(message, p1, p2, game_id)
                log.info(f"Winning Discord Player: {winning_player}")
            elif p1.handicap:
                log.info("Player 1 is handicapped")
                game_link, game_id = await lichess.challenge(p1.token, p2.lichess, 120)
                await message.channel.send(f'Link: <{game_link}>')
                await self.handicap_start(game_id=game_id, handicap_player=p1, stronger_player=p2)
                winning_player = await self.decide_winner(message, p1, p2, game_id)
                log.info(f"Winning Discord Player: {winning_player}")
                if winning_player == p1:
                    item = {
                        "handicap_player": p1.lichess,
                        "stronger_player": p2.lichess
                    }
                    dynamodb.update_score(item, 1, "scores")
            elif p2.handicap:
                log.info("Player 2 is handicapped")
                game_link, game_id = await lichess.challenge(p1.token, p2.lichess, 120)
                await message.channel.send(f'Link: <{game_link}>')
                await self.handicap_start(game_id=game_id, handicap_player=p2, stronger_player=p1)
                winning_player = await self.decide_winner(message, p1, p2, game_id)
                log.info(f"Winning Discord Player: {winning_player}")
                if winning_player == p2:
                    item = {
                        "handicap_player": p2.lichess,
                        "stronger_player": p1.lichess
                    }
                    dynamodb.update_score(item, 1, "scores")
            else:
                game_link, game_id = await lichess.challenge(p1.token, p2.lichess, 300)
                await message.channel.send(f'Link: <{game_link}>')
                winning_player = await self.decide_winner(message, p1, p2, game_id)
                log.info(f"Winning Discord Player: {winning_player}")

        except Exception as err:
            log.error(err)
            await message.channel.send(err)

    async def handicap_start(self, game_id: str, handicap_player: Player, stronger_player: Player):
        """
        Starts Handicap Match
        @param game_id:
        @param handicap_player:
        @param stronger_player:
        @param start:
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

    async def decide_winner(self, message, p1: Player, p2: Player, game_id: str):
        log.info("Deciding on discord winner")
        winner = await lichess.get_result(game_id)
        if p1.lichess == winner.lower():
            log.info(f"Discord Player1: {p1.discord}")
            await message.channel.send(f'{p1.discord} won!')
            return p1
        else:
            log.info(f"Discord Player2: {p2.discord}")
            await message.channel.send(f'{p2.discord} won!')
            return p2


def setup(bot):
    bot.add_cog(Game(bot))
