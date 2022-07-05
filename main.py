from app.bot import MyClient
from dotenv import load_dotenv
import os

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

client = MyClient()
client.run(DISCORD_TOKEN)
client.run()

