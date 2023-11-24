import json

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.db.models import User, FavoriteRoute
from app.bot import texts


def start_menu(to_user: User) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=texts.favorite_routes_button, callback_data=f"get_favorites_{to_user.tg_id}"))
    keyboard.add(InlineKeyboardButton(text=texts.get_route_schedule, callback_data=f"new_route"))
    return keyboard


# def pick_region() -> InlineKeyboardMarkup:
#     keyboard = InlineKeyboardMarkup()
#     with open("./app/data/data_russia_trains.json") as file:
#         data = json.load(file)
#         for i in data.keys():
#             keyboard.add(InlineKeyboardButton(text=i, callback_data=f"region_{i}"))
#     return keyboard


async def favorite_routes(to_user: User) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    routes = await FavoriteRoute.filter(user_id=to_user.uuid)

    for i in routes:
        keyboard.add(InlineKeyboardButton(text=texts.get_route_text(i.start_station, i.finish_station), 
                                          callback_data=f"route_{i.start_station}_to_{i.finish_station}"))
    
    keyboard.add(InlineKeyboardButton(text=texts.back_to_welcome_menu, callback_data=f"back_to_start_menu"))

    return keyboard


async def get_regions() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    with open("./app/data/data_russia_trains.json") as f:
        data = json.load(f)
        for key in sorted(data.keys()):
            keyboard.add(InlineKeyboardButton(text=f"{key}", callback_data=f"region_{key}"))

    keyboard.add(InlineKeyboardButton(text=texts.back_to_welcome_menu, callback_data=f"back_to_start_menu"))

    return keyboard