import logging
import os
from enum import Enum
from shutil import SameFileError

from app.engine import Engine
from app.storage import Metadata
from dotenv import load_dotenv
from telegram import InputMediaPhoto, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

TG_HELLO = "Здарова братан, чем могу помочь?"
TG_THANK = "От души, ждем чудес!"
TG_LOST_PET = "Я потерял своего дружочка"
TG_FOUND_PET = "Я нашел чужого дружочка"
TG_SEND_ME = "Пришли фотографию питомца в анфас"
TG_PHOTO_PATH = "./photos"


class Action(Enum):
    ADD = 0
    FIND = 1


global chat_to_action
chat_to_action = {}

global engine
engine = Engine()


def msg(update, context):
    text = update.message.text
    chat_id = update.effective_chat.id

    if text == TG_LOST_PET:
        chat_to_action[chat_id] = Action.FIND
    elif text == TG_FOUND_PET:
        chat_to_action[chat_id] = Action.ADD
    else:
        return

    context.bot.send_message(chat_id=update.effective_chat.id, text=TG_SEND_ME)


def img(update, context):
    tg_file = update.message.photo[-1].get_file()
    filename = os.path.join(TG_PHOTO_PATH, os.path.basename(tg_file.file_path))
    try:
        tg_file.download(custom_path=filename)
    except SameFileError:
        pass

    chat_id = update.effective_chat.id
    meta = Metadata(filename, chat_id, update.message.message_id,
                    {"username": update.effective_chat.username})
    if chat_to_action[chat_id] == Action.FIND:
        __find(update, context, meta)
    elif chat_to_action[chat_id] == Action.ADD:
        __add(update, context, meta)


def start(update, context):
    start_keyboard = [[TG_LOST_PET, TG_FOUND_PET]]

    markup = ReplyKeyboardMarkup(keyboard=start_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=False)

    context.bot.send_message(chat_id=update.effective_chat.id,
                             reply_markup=markup,
                             text=TG_HELLO)


def __add(update, context, meta):
    engine.add(meta)
    context.bot.send_message(chat_id=update.effective_chat.id, text=TG_THANK)


def __find(update, context, meta):
    k_nbrs = engine.search(meta)

    matches = []
    for i, (dist, meta) in enumerate(k_nbrs):
        with open(meta.filename, 'rb') as f:
            matches.append((f.read(), meta.other["username"], dist))

    to_send = [
        InputMediaPhoto(
            p, caption=f"User: @{username}, L2 distance: {dist}")
        for p, username, dist in matches
    ]

    context.bot.send_media_group(chat_id=update.effective_chat.id,
                                 media=to_send)


if __name__ == "__main__":
    load_dotenv()

    updater = Updater(token=os.environ["TOKEN"], use_context=True)

    dispatcher = updater.dispatcher

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    msg_handler = MessageHandler(Filters.text & ~Filters.command, msg)
    dispatcher.add_handler(msg_handler)

    img_handler = MessageHandler(Filters.photo, img)
    dispatcher.add_handler(img_handler)

    updater.start_polling()
