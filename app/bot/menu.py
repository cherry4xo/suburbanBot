import json

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.db.models import User, FavoriteRoute
from app.bot import texts


def start_menu(to_user: User) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=texts.favorite_routes_button, callback_data=f"get_favorites_{to_user.uuid}"))
    keyboard.add(InlineKeyboardButton(text=texts.get_route_schedule, callback_data=f"new_route"))


def pick_region() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    with open("./app/data/data_russia_trains.json") as file:
        data = json.load(file)
        for i in data.keys():
            keyboard.add(InlineKeyboardButton(text=i, callback_data=f"region_{i}"))


