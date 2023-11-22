from telebot.async_telebot import AsyncTeleBot
import telebot
import os
import secrets
import time
import asyncio

from app.db.init_db import init
from app.db.models import User
from app.db.schemas import BaseUserCreate
from app.bot import texts
from app.bot import menu
from app.settings.config import settings

bot = AsyncTeleBot(settings.TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=["start"])
async def welcome(message: telebot.types.Message):
    uid = int(message.from_user.id)

    user = await User.get_by_tg_id(uid)

    if not user:
        username = message.from_user.username
        first_name = message.from_user.first_name
        user = await User.create(**BaseUserCreate(tg_id=uid, first_name=first_name, username=username).model_dump())

        await bot.send_message(user.tg_id, texts.first_join(user.first_name), reply_markup=menu.start_menu)

    else:
        await bot.send_message(user.tg_id, texts.welcome_text(user.first_name), reply_markup=menu.start_menu)


if __name__ == "__main__": 
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    asyncio.run(init())
    while True:
        try:
            asyncio.run(bot.polling(none_stop=True))
        except Exception as e:
            delay = 3
            text = f'Error: {e}, restarting after {delay} seconds'
            print(text)
            time.sleep(delay)
            text = f'Restarted'
            print(text)