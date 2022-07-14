from pydantic import BaseModel


class Player(BaseModel):
    lichess: str
    discord_id: str
    handicap: bool = False
    token: str
    discord: str

