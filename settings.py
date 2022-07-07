"""Settings for bot from .env"""
from dotenv import load_dotenv
import os


load_dotenv()


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BOT_PREFIX = os.getenv("BOT_PREFIX")