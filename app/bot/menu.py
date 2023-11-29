import json

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.db.models import User, FavoriteRoute
from app.bot import texts


def start_menu(to_user: User) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=texts.favorite_routes_button, callback_data=f"get_favorites_{to_user.tg_id}"))
    keyboard.add(InlineKeyboardButton(text=texts.get_route_schedule, callback_data=f"new_route"))
    return keyboard


def from_favorites(to_user: User, start_id: str, finish_id: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=texts.remove_from_favorites, callback_data=f"rm_{start_id}_{finish_id}"))
    keyboard.add(InlineKeyboardButton(text=texts.back_to_favorites, callback_data=f"get_favorites_{to_user.tg_id}"))
    keyboard.add(InlineKeyboardButton(text=texts.back_to_welcome_menu, callback_data=f"back_to_start_menu"))

    return keyboard


async def favorite_routes(to_user: User) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    routes = await FavoriteRoute.filter(user_id=to_user.uuid)

    for i in routes:
        added_stations_titles = {}

        with open("./app/data/data_russia_trains.json", "r") as f:
            data = json.load(f)
            for region_title, region_data in data.items():
                for station in region_data:
                    if i.start_station == station["id"]:
                        added_stations_titles.update({"start": station["title"]})
                    if i.finish_station == station["id"]:
                        added_stations_titles.update({"finish": station["title"]})

        keyboard.add(InlineKeyboardButton(text=texts.get_route_text(added_stations_titles["start"], added_stations_titles["finish"]), 
                                          callback_data=f"route_{i.start_station}_{i.finish_station}"))
    
    keyboard.add(InlineKeyboardButton(text=texts.back_to_welcome_menu, callback_data=f"back_to_start_menu"))

    return keyboard


def searched_start_stations(stations: list) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    
    for station in stations:
        keyboard.add(InlineKeyboardButton(text=texts.get_station_text(station["title"], station["region_title"]), 
                                          callback_data=f"start_\"{station['title']}\"_{station['id']}"))
    
    keyboard.add(InlineKeyboardButton(text=texts.cancel_search, callback_data=f"new_route"))

    return keyboard


def searched_finish_stations(stations: list) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    for station in stations:
        keyboard.add(InlineKeyboardButton(text=texts.get_station_text(station["title"], station["region_title"]), 
                                          callback_data=f"finish_\"{station['title']}\"_{station['id']}"))
    
    keyboard.add(InlineKeyboardButton(text=texts.cancel_search, callback_data=f"new_route"))

    return keyboard


def schedule(start_id, finish_id) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    # keyboard.add(InlineKeyboardButton(text=texts.add_route_to_favorites, callback_data=f"addtofavorites_{to_user}_{start_station_id}_{finish_station_id}_{start_station}_{finish_station}"))
    keyboard.add(InlineKeyboardButton(text=texts.add_route_to_favorites, callback_data=f"addf_{start_id}_{finish_id}"))
    keyboard.add(InlineKeyboardButton(text=texts.back_to_welcome_menu, callback_data=f"back_to_start_menu"))

    return keyboard

def go_to_main_menu_only():
    keyboard = InlineKeyboardMarkup()
    
    keyboard.add(InlineKeyboardButton(text=texts.back_to_welcome_menu, callback_data=f"back_to_start_menu"))

    return keyboard