import telebot
import os
import json
import secrets
import time
import asyncio
import aiohttp

from datetime import date, datetime, timedelta
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_filters import StateFilter
from telebot.asyncio_handler_backends import State, StatesGroup
from tortoise import run_async
from pydantic import UUID4

from app.db.init_db import init
from app.db.models import User
from app.db.schemas import BaseUserCreate
from app.bot import texts
from app.bot import menu
from app.settings.config import settings

state_storage = StateMemoryStorage()

bot = AsyncTeleBot(settings.TELEGRAM_BOT_TOKEN, state_storage=state_storage)


class States(StatesGroup):
    search_start_station = State()
    search_finish_station = State()

async def get_schedule_request(session, to_user: User, start_station_id: str, finish_station_id: str):
    url = f"https://api.rasp.yandex.net/v3.0/search/?apikey={settings.YANDEX_API_TOKEN}&format=json&from={start_station_id}&to={finish_station_id}&lang=ru_RU&page=1&date={date.isoformat(date.today())}"
    try:
        async with session.get(url=url) as response:
            return await response.json()
    except BaseException:
        bot.send_message(to_user.tg_id, text=texts.cannot_get_schedule, reply_markup=menu.go_to_main_menu_only())


async def get_schedule_task(to_user: User, start_station_id: str, finish_station_id: str):
    async with aiohttp.ClientSession(headers={"Accept": "application/json"}) as session:
        task = get_schedule_request(session, to_user, start_station_id, finish_station_id)
        return await asyncio.gather(task)
    

def schedule_filter(trip: dict):
    return datetime.fromisoformat(trip["departure"]).strftime("%Y-%m-%d %H:%M:%S") > (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")


def get_normalized_schedule_response(schedule: dict) -> dict:
    norm_schedule = []
    for train in list(filter(schedule_filter, schedule["segments"]))[:3]:
        trip = {"number": train["thread"]["number"],
                "title": train["thread"]["title"],
                "train_subtype": train["thread"]["transport_subtype"]["title"],
                "stops": train["stops"],
                "from": train["from"]["title"],
                "to": train["to"]["title"],
                "departure_platform": train["departure_platform"],
                "arrival_platform": train["arrival_platform"],
                "departure_time": train["departure"],
                "arrival_time": train["arrival"],
                "duration": train["duration"]}
        
        norm_schedule.append(trip)
        
    return norm_schedule


async def user_does_not_exist_message(id: int):
    await bot.send_message(id, 
                           texts.user_does_not_exist(id), 
                           reply_markup=menu.start_menu(id))


temp_station_search = dict()


@bot.message_handler(commands=["start"])
async def welcome(message: telebot.types.Message):
    
    uid = int(message.from_user.id)
    user = await User.get_by_tg_id(uid)

    if not user:
        username = message.from_user.username
        first_name = message.from_user.first_name
        user = await User.create(BaseUserCreate(tg_id=uid, first_name=first_name, username=username))
        message = await bot.send_message(user.tg_id, texts.first_join(user.first_name), reply_markup=menu.start_menu(user))
    else:
        message = await bot.send_message(user.tg_id, texts.welcome_text(user.first_name), reply_markup=menu.start_menu(user))


@bot.message_handler(state=States.search_start_station)
async def search_start_station(msg: telebot.types.Message):
    search_list = []  
    with open("./app/data/data_russia_trains.json", "r") as f:
        data = json.load(f)
        for region_title, region_data in data.items():
            for station in region_data:
                if msg.text.lower() in station["title"].lower():
                    search_list.append({"title": station["title"], 
                                        "id": station["id"], 
                                        "region_title": region_title})

    await bot.delete_state(msg.from_user.id, msg.chat.id)
    await bot.send_message(msg.chat.id,
                           text=texts.choose_start_station,
                           reply_markup=menu.searched_start_stations(search_list))


@bot.message_handler(state=States.search_finish_station)
async def search_finish_station(msg: telebot.types.Message):
    search_list = []  
    with open("./app/data/data_russia_trains.json", "r") as f:
        data = json.load(f)
        for region_title, region_data in data.items():
            for station in region_data:
                if msg.text.lower() in station["title"].lower():
                    search_list.append({"title": station["title"], 
                                        "id": station["id"], 
                                        "region_title": region_title})

    await bot.send_message(msg.chat.id,
                           text=texts.choose_finish_station,
                           reply_markup=menu.searched_finish_stations(search_list))


@bot.callback_query_handler(func=lambda call: call.data.startswith("get_favorites_"))
async def get_favorites_callback_handler(call: telebot.types.CallbackQuery):
    user = await User.get_by_tg_id(call.from_user.id)

    if user is None:
        await user_does_not_exist_message(call.from_user.id) 
    else:
        await bot.send_message(user.tg_id, 
                               texts.favorite_routes_response, 
                               reply_markup=await menu.favorite_routes(user))
        

@bot.callback_query_handler(func=lambda call: call.data.startswith("back_to_start_menu"))
async def start_menu_callback_handler(call: telebot.types.CallbackQuery):
    uid = int(call.from_user.id)
    user = await User.get_by_tg_id(uid)

    if not user:
        username = message.from_user.username
        first_name = message.from_user.first_name
        user = await User.create(BaseUserCreate(tg_id=uid, first_name=first_name, username=username))
        message = await bot.send_message(user.tg_id, texts.first_join(user.first_name), reply_markup=menu.start_menu(user))
    else:
        message = await bot.send_message(user.tg_id, texts.welcome_text(user.first_name), reply_markup=menu.start_menu(user))


@bot.callback_query_handler(func=lambda call: call.data.startswith("new_route"))
async def new_route_callback_handler(call: telebot.types.CallbackQuery):
    user = await User.get_by_tg_id(call.from_user.id)
        
    if not user:
        await user_does_not_exist_message(call.from_user.id)

    await bot.set_state(user.tg_id, States.search_start_station, call.message.chat.id)
    await bot.send_message(call.message.chat.id, text=texts.search_start_station, reply_markup=menu.go_to_main_menu_only())


@bot.callback_query_handler(func=lambda call: call.data.startswith("startstation_"))
async def pick_finish_station_callback_handler(call: telebot.types.CallbackQuery):
    user = await User.get_by_tg_id(call.from_user.id)
        
    if not user:
        await user_does_not_exist_message(call.from_user.id)

    data = call.data.split('_')[1:]
    start_station_title = data[0][1:-1]
    start_station_id = data[1]

    temp_station_search.update({user.tg_id: {"title": start_station_title, 
                                             "id": start_station_id}})

    await bot.set_state(user.tg_id, States.search_finish_station, call.message.chat.id)
    await bot.send_message(call.message.chat.id, text=texts.search_finish_station, reply_markup=menu.go_to_main_menu_only())


@bot.callback_query_handler(func=lambda call: call.data.startswith("finishstation_"))
async def make_route_callback_handler(call: telebot.types.CallbackQuery):
    user = await User.get_by_tg_id(call.from_user.id)

    if not user:
        await user_does_not_exist_message(call.from_user.id)

    data = call.data.split('_')[1:]
    finish_station_title = data[0][1:-1]
    finish_station_id = data[1]

    start_station_data = temp_station_search.pop(user.tg_id)

    schedule = await get_schedule_task(user, start_station_data["id"], finish_station_id)

    normalized_schedule = get_normalized_schedule_response(schedule[0])

    await bot.send_message(call.message.chat.id, 
                           text=texts.get_schedule(normalized_schedule), 
                           reply_markup=menu.schedule(user, 
                                                      start_station_data["id"], 
                                                      finish_station_id, 
                                                      start_station_data["title"],
                                                      finish_station_title))


if __name__ == "__main__":

    bot.add_custom_filter(StateFilter(bot))
    run_async(init())
    while True:
        try:
            run_async(bot.polling(none_stop=True))
        except Exception as e:
            delay = 3
            text = f'Error: {e}, restarting after {delay} seconds'
            print(text)
            time.sleep(delay)
            text = f'Restarted'
            print(text)