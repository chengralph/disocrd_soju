import requests
import json
from lichess_client import APIClient
from lichess_client.utils.enums import StatusTypes
import aiohttp
from app.models.models import Player
from app.common.log import get_logger

log = get_logger()


class LiChess:
    def __init__(self):
        self.lichess_client = None
        self.content_challenge = None
        self.default_time = 120

    async def auth(self, lichess_token):
        self.lichess_client = APIClient(token=lichess_token)
        response = await self.lichess_client.account.get_my_profile()
        if response.entity.status == StatusTypes.SUCCESS:
            log.info("Auth Successful")
            return response.entity.content['id']
        else:
            log.info("Auth Declined")
            return False

    async def challenge(self, lichess_token, username: str, time_limit: int):
        await self.auth(lichess_token)
        response = await self.lichess_client.challenges.create(username=username, time_limit=time_limit, time_increment=0)
        print(f"Challenge response: {response}")
        if response.entity.status == StatusTypes.SUCCESS:
            print("Challenge")
            self.content_challenge = response.entity.content["challenge"]
            return self.content_challenge["url"], self.content_challenge["id"]
        raise Exception

    async def time_calculation(self, p1: Player, p2: Player):
        with open("scores.json", "r+") as json_file:
            data = json.load(json_file)
            if p1.handicap and p2.handicap:
                return 600, 600

            if p1.lichess in data:
                losses = data[p1.lichess][p2.lichess]
                p1_time = (17 * 60) - (losses * 60)
                p2_time = self.default_time + (losses * 15)
                return p2_time, p1_time
            elif p2.lichess in data:
                losses = data[p2.lichess][p1.lichess]
                p2_time = (17 * 60) - (losses * 60)
                p1_time = self.default_time + (losses * 15)
                return p1_time, p2_time
            else:
                if p1.handicap:
                    data_obj = {
                        p2.lichess: {
                            p1.lichess: 0,
                        }
                    }
                elif p2.handicap:
                    data_obj = {
                        p1.lichess: {
                            p2.lichess: 0,
                        }
                    }
                data.update(data_obj)
                json_file.seek(0)
                json.dump(data, json_file, indent=4)
                json_file.truncate()
                return self.default_time, 900

    async def time_appropriation(self, lichess_token, game_id, seconds):
        headers = {
            'Authorization': f'Bearer {lichess_token}',
            'Content-Type': 'application/json'
        }

        while True:
            response = requests.post(url=f"https://lichess.org/api/round/{game_id}/add-time/{seconds}",
                                     headers=headers)
            if response.ok:
                print(f"Time Added: {response}")
                break

    async def get_result(self, game_id):
        print("Getting result")

        async with aiohttp.request('get', f'https://lichess.org/api/stream/game/{game_id}') as r:
            async for line in r.content:
                try:
                    json_data = json.loads(line)
                    print(json_data)
                    winner = json_data.get("winner", None)
                    if winner:
                        print(f"Winner was: {winner}")
                except Exception:
                    continue


