import logging
import os
import zipfile
from enum import Enum
from shutil import SameFileError

from app.engine import Action, Engine
from app.storage import Metadata
from dotenv import load_dotenv
from telegram import InputMediaPhoto, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

TG_HELLO = "Здарова братан, чем могу помочь?"
TG_THANK = "От души, ждем чудес!"
TG_SUCCESS_ADD = "Питомец успешно добавлен в базу"
TG_LOST_PET = "Я потерял своего дружочка"
TG_FOUND_PET = "Я нашел чужого дружочка"
TG_SEND_ME = "Пришли мордочку питомца в анфас"
TG_NO_MATCHES = "Совпадений не найдено :("
TG_CHOOSE_ACTION = "Сначала выбери действие"
TG_PHOTO_PATH = "./photos"

global chat_to_action
chat_to_action = {}

global engine
engine = Engine(os.environ["FOUND_STORAGE_URL"],
                os.environ["LOST_STORAGE_URL"])


def msg(update, context):
    text = update.message.text
    chat_id = update.effective_chat.id

    if text == TG_LOST_PET:
        chat_to_action[chat_id] = Action.LOST
    elif text == TG_FOUND_PET:
        chat_to_action[chat_id] = Action.FOUND
    else:
        return

    context.bot.send_message(chat_id=update.effective_chat.id, text=TG_SEND_ME)


def img(update, context):
    chat_id = update.effective_chat.id
    if chat_id not in chat_to_action:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=TG_CHOOSE_ACTION)
        return

    tg_file = update.message.photo[-1].get_file()
    filename = os.path.join(TG_PHOTO_PATH, os.path.basename(tg_file.file_path))
    try:
        tg_file.download(custom_path=filename)
    except SameFileError:
        pass

    meta = Metadata(filename, chat_id, update.message.message_id,
                    {"username": update.effective_chat.username})

    action = chat_to_action[chat_id]
    __find(update, context, meta, action)
    __add(update, context, meta, action)


def doc(update, context):
    chat_id = update.effective_chat.id
    if chat_id not in chat_to_action:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=TG_CHOOSE_ACTION)
        return

    tg_file = update.message.document.get_file()
    basename = os.path.basename(tg_file.file_path)
    if basename.split('.')[1] != 'zip':
        return

    action = chat_to_action[chat_id]
    filename = os.path.join(TG_PHOTO_PATH, basename)
    try:
        tg_file.download(custom_path=filename)
        with zipfile.ZipFile(filename, "r") as zip_ref:
            zip_ref.extractall(TG_PHOTO_PATH)
            for info in zip_ref.filelist:
                meta = Metadata(os.path.join(TG_PHOTO_PATH, info.filename),
                                chat_id, update.message.message_id,
                                {"username": update.effective_chat.username})
                __add(update, context, meta, action, True)
    except SameFileError:
        pass

    context.bot.send_message(chat_id=update.effective_chat.id, text="Готово")


def start(update, context):
    start_keyboard = [[TG_LOST_PET, TG_FOUND_PET]]

    markup = ReplyKeyboardMarkup(keyboard=start_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=False)

    context.bot.send_message(chat_id=update.effective_chat.id,
                             reply_markup=markup,
                             text=TG_HELLO)


def __add(update, context, meta, action, silent=False):
    engine.add(meta, action)

    if not silent:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=TG_SUCCESS_ADD)


def __find(update, context, meta, action):
    k_nbrs = engine.search(meta, action)

    matches = []
    for i, (dist, meta) in enumerate(k_nbrs):
        with open(meta.filename, 'rb') as f:
            matches.append((f.read(), meta.other["username"], dist))

    if not matches:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=TG_NO_MATCHES)
        return

    to_send = [
        InputMediaPhoto(p,
                        caption=f"User: @{username}, L2 distance: {dist:.2f}")
        for p, username, dist in matches
    ]

    context.bot.send_media_group(chat_id=update.effective_chat.id,
                                 media=to_send)


if __name__ == "__main__":
    if not os.path.exists(TG_PHOTO_PATH):
        os.makedirs(TG_PHOTO_PATH)

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

    doc_handler = MessageHandler(Filters.document, doc)
    dispatcher.add_handler(doc_handler)

    updater.start_polling()
