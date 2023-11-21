import os

from decouple import config

import string
import random


class Settings:
    YANDEX_API_TOKEN = config("YANDEX_API_TOKEN")
    TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")

settings = Settings()