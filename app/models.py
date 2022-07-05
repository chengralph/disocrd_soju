from pydantic import BaseModel


class Player(BaseModel):
    lichess: str
    discord: str
    token: str
    handicap: bool = False
