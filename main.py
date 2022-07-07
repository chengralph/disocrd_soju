from app.bot import MyClient
from dotenv import load_dotenv
import os
from app.aws.dynamodb import get_items_from_dynamodb


load_dotenv()
# DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
#
# client = MyClient()
# client.run(DISCORD_TOKEN)
# client.run()

print(get_items_from_dynamodb("players"))
