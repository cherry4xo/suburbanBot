import telebot
import os
import secrets
import time
import asyncio
from telebot.async_telebot import AsyncTeleBot
from tortoise import run_async
from pydantic import UUID4

from app.db.init_db import init
from app.db.models import User
from app.db.schemas import BaseUserCreate
from app.bot import texts
from app.bot import menu
from app.settings.config import settings

bot = AsyncTeleBot(settings.TELEGRAM_BOT_TOKEN)


async def user_does_not_exist_message(id: int):
    await bot.send_message(id, 
                           texts.user_does_not_exist(id), 
                           reply_markup=menu.start_menu(id))


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


async def search_station(message: telebot.types.Message):
    pass


@bot.callback_query_handler(func=lambda call: True)
async def callback_handler(call: telebot.types.CallbackQuery):
    if call.data.startswith("get_favorites_"):
        user = await User.get_by_tg_id(call.from_user.id)

        if user is None:
            await user_does_not_exist_message(call.from_user.id) 
        else:
            await bot.send_message(user.tg_id, 
                                   texts.favorite_routes_response, 
                                   reply_markup=await menu.favorite_routes(user))
            
    if call.data.startswith("back_to_start_menu"):
        uid = int(call.from_user.id)
        user = await User.get_by_tg_id(uid)

        if not user:
            username = message.from_user.username
            first_name = message.from_user.first_name
            user = await User.create(BaseUserCreate(tg_id=uid, first_name=first_name, username=username))
            message = await bot.send_message(user.tg_id, texts.first_join(user.first_name), reply_markup=menu.start_menu(user))
        else:
            message = await bot.send_message(user.tg_id, texts.welcome_text(user.first_name), reply_markup=menu.start_menu(user))

    if call.data.startswith("new_route"):
        user = await User.get_by_tg_id(call.from_user.id)
        await bot.send_message(user.tg_id, texts.pick_region, reply_markup=await menu.get_regions())


    if call.data.startswith("region_"):
        user = await User.get_by_tg_id(call.from_user.id)
        
        if not user:
            await user_does_not_exist_message(call.from_user.id)
        
        # start_station = bot.edit_message




if __name__ == "__main__":
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