import logging
import os
from dotenv import load_dotenv

from enum import Enum

from telegram import InputMediaPhoto, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from config import TG_FOUND_PET, TG_HELLO, TG_LOST_PET, TG_PHOTO_PATH, TG_SEND_ME, TG_THANK
from engine import Engine


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

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=TG_SEND_ME)


def img(update, context):
    tg_file = update.message.photo[-1].get_file()
    path = os.path.join(TG_PHOTO_PATH, os.path.basename(tg_file.file_path))
    file = tg_file.download(custom_path=path)

    chat_id = update.effective_chat.id
    if chat_to_action[chat_id] == Action.FIND:
        __find(update, context, file)
    elif chat_to_action[chat_id] == Action.ADD:
        __add(update, context, file)


def start(update, context):
    start_keyboard = [[TG_LOST_PET, TG_FOUND_PET]]

    markup = ReplyKeyboardMarkup(keyboard=start_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=False)

    context.bot.send_message(chat_id=update.effective_chat.id,
                             reply_markup=markup,
                             text=TG_HELLO)


def __add(update, context, file):
    engine.add(file)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=TG_THANK)


def __find(update, context, file):
    k_nbrs = engine.search(file)

    photos_bin = []
    caption = ""
    for i, (dist, file) in enumerate(k_nbrs):
        caption += f"{i+1}. L2 distance = [{dist:.3f}]\n"
        with open(file, 'rb') as f:
            photos_bin.append((f.read(), dist))

    to_send = [InputMediaPhoto(p, caption=f"L2 distance={dist}") for p, dist in photos_bin]

    context.bot.send_media_group(chat_id=update.effective_chat.id,
                                 media=to_send)


if __name__ == "__main__":
    load_dotenv()

    updater = Updater(token=os.environ["TOKEN"],
                      use_context=True)

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
