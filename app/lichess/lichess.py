import json
import chess.pgn
import io
import aiohttp
import requests
from lichess_client import APIClient
from lichess_client.utils.enums import StatusTypes

from app.aws import dynamodb
from app.common.log import get_logger
from app.models.models import Player

log = get_logger("standard")


class LiChess:
    def __init__(self):
        self.lichess_client = None
        self.content_challenge = None

    async def auth(self, lichess_token):
        """
        Authorize Lichess Token
        @param lichess_token:
        @return:
        """
        self.lichess_client = APIClient(token=lichess_token)
        response = await self.lichess_client.account.get_my_profile()
        if response.entity.status == StatusTypes.SUCCESS:
            log.info("Lichess Auth Successful")
            return response.entity.content['id']
        else:
            log.info("Lichess Auth Declined")
            return False

    async def challenge(self, lichess_token, username: str, time_limit: int):
        """
        Creates Lichess challenge
        @param lichess_token:
        @param username:
        @param time_limit:
        @return:
        """
        await self.auth(lichess_token)
        response = await self.lichess_client.challenges.create(username=username, time_limit=time_limit,
                                                               time_increment=0, color="random")
        print(f"Challenge response: {response}")
        if response.entity.status == StatusTypes.SUCCESS:
            print("Challenge")
            self.content_challenge = response.entity.content["challenge"]
            return self.content_challenge["url"], self.content_challenge["id"]
        raise Exception

    async def calculate_bonus_time(self, handicap_player: Player, stronger_player: Player):
        """
        Calculates the bonus time for handicap player and stronger palyer
        @param handicap_player:
        @param stronger_player:
        @return handicap_bonus_time, stronger_bonus_time:
        """
        log.info("Calculate bonus time")
        scores = dynamodb.get_items("scores")

        score = [i for i in scores if
                 i["handicap_player"] == handicap_player.lichess and
                 i["stronger_player"] == stronger_player.lichess]
        log.info(f"Score: {score}")
        if score:
            # losses for stronger player
            losses = score[0]["score"]
            # Equilibrium time is 5min. Stronger player starts at 2min vs Handicap Player at 17min.
            # Each stronger player loss results in 15 seconds added to stronger_time
            # and 1 minute subtracted from handicap_time
            losses = min(losses, 12)
            handicap_bonus_time = (15 * 60) - (losses * 60)
            stronger_bonus_time = losses * 15

            return handicap_bonus_time, stronger_bonus_time if stronger_bonus_time else 1
        else:
            item = {
                "handicap_player": handicap_player.lichess,
                "stronger_player": stronger_player.lichess,
                "score": 0,
            }
            log.info(f'Score initiated and set to 0')
            dynamodb.put_item("scores", item)
            # Equilibrium time is 5min. Stronger player starts at 2min vs Handicap Player at 17min.
            # Returns handicap_bonus_time, stronger_bonus_time
            return 12*60, 1

    async def appropriate_time(self, lichess_token: str, game_id: str, seconds: int):
        """
        Adds time to a player.
        @param lichess_token:
        @param game_id:
        @param seconds:
        @return:
        """
        log.info("Time Appropriation. Adding time...")
        headers = {
            'Authorization': f'Bearer {lichess_token}',
            'Content-Type': 'application/json'
        }

        while True:
            response = requests.post(url=f"https://lichess.org/api/round/{game_id}/add-time/{seconds}",
                                     headers=headers)
            if response.ok:
                log.info(f"Time Added: {response.json()}")
                break

    async def get_result(self, game_id: str):
        log.info("Getting result")

        async with aiohttp.request('get', f'https://lichess.org/api/stream/game/{game_id}') as r:
            async for line in r.content:
                try:
                    json_data = json.loads(line)
                    log.info(json_data)
                    winner = json_data.get("winner", None)
                    if winner:
                        log.info(f"Winner was: {winner}")
                except Exception as err:
                    log.info(f"Exception from async get result: {err}")
                    continue

        game = await self.lichess_client.games.export_one_game(game_id=game_id)
        log.info(game.entity.content)
        white = game.entity.content.headers["White"]
        black = game.entity.content.headers["Black"]
        game_result = game.entity.content.headers['Result']
        if game_result[0] == "1":
            log.info(f"{white} wins!")
            return white
        else:
            log.info(f"{black} wins!")
            return black
