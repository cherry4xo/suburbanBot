import telebot
import os
import json
import secrets
import time
import asyncio
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
    with open("./app/data/data_russia_trains.json", "r") as f:
        data = json.load(f)
        for region_title, region_data in data.items():
            for station in region_data:
                if msg.text.lower() in station["title"].lower():
                    temp_station_search.update({msg.from_user.id: {"title": station["title"], 
                                                                   "id": station["id"], 
                                                                   "region_title": region_title}})
    await bot.set_state(msg.from_user.id, States.search_finish_station, msg.chat.id)
    print(temp_station_search)


@bot.message_handler(state=States.search_finish_station)
async def search_finish_station(msg: telebot.types.Message) -> list:
    with open("./app/data/data_russia_trains.json", "r") as f:
        data = json.load(f)
        for region_title, region_data in data.items():
            for station in region_data:
                if msg.text.lower() in station["title"].lower():
                    temp_station_search.update({msg.from_user.id: {"title": station["title"], 
                                                                   "id": station["id"], 
                                                                   "region_title": region_title}})
    await bot.set_state(msg.from_user.id, States.search_finish_station, msg.chat.id)

    await bot.send_message(msg.chat.id, text=texts.search_finish_station)


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


# @bot.callback_query_handler(func=lambda call: call.data.startswith("new_route"))
# async def new_route_callback_handler(call: telebot.types.CallbackQuery):
#     user = await User.get_by_tg_id(call.from_user.id)
#     await bot.send_message(user.tg_id, texts.pick_region, reply_markup=await menu.get_regions())


@bot.callback_query_handler(func=lambda call: call.data.startswith("new_route"))
async def pick_region_callback_handler(call: telebot.types.CallbackQuery):
    user = await User.get_by_tg_id(call.from_user.id)
        
    if not user:
        await user_does_not_exist_message(call.from_user.id)

    await bot.send_message(call.message.chat.id, text=texts.search_start_station)
    await bot.set_state(user.tg_id, States.search_start_station, call.message.chat.id)


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