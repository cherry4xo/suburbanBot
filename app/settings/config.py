import os

from decouple import config

import string
import random


class Settings:
    YANDEX_API_TOKEN = config("YANDEX_API_TOKEN")
    TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")

    DB_NAME = config("DB_NAME")
    DB_USER = config("DB_USER")
    DB_PASS = config("DB_PASS")
    DB_HOST = config("DB_HOST")
    DB_PORT = config("DB_PORT")

    DB_URL = f"posgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    APPLICATIONS = [
        "db"
    ]

    APPLICATIONS_MODULE = "app"


settings = Settings()