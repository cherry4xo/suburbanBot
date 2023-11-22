import telebot
import os
import menu
import secrets
import time

from app.db.init_db import init
from app.db.models import User
from app.db.schemas import BaseUserCreate
from app.bot import texts
from app.bot import menu
from app.settings.config import settings

init()

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)


@bot.message_handler(commands=["start"])
async def welcome(message: telebot.types.Message):
    uid = int(message.from_user.id)

    user = await User.get_by_tg_id(uid)

    if not user:
        username = message.from_user.username
        first_name = message.from_user.first_name
        user = await User.create(**BaseUserCreate(tg_id=uid, first_name=first_name, username=username).model_dump())

        bot.send_message(user.tg_id, texts.first_join(user.first_name), reply_markup=None)

    else:
        bot.send_message(user.tg_id, texts.welcome_text(user.first_name), reply_markup=None)