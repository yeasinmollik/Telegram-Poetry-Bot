from requests import request

from helper import authors, p_url, p_headers
import json
import logging
import os
import pprint
import random
from time import sleep
from typing import List, Tuple, cast
from telegram.chataction import ChatAction
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    InvalidCallbackData,
    PicklePersistence,
    MessageHandler,
    Filters,
    ConversationHandler,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

BY_AUTHOR, BY_TITLE, BROWSE_AUTHORS, RANDOM, CANCEL = "byAuthor", "byTitle", "browseAuthors", "random", "cancel"

TYPE = range(1)

# url and headers for PoetryDB api
poetry_url = p_url
poetry_headers = p_headers


def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton('Random', callback_data=RANDOM)],
                [
                    InlineKeyboardButton('Search Title',
                                         callback_data=BY_TITLE),
                    InlineKeyboardButton('Search Author',
                                         callback_data=BY_AUTHOR)
                ],
                [
                    InlineKeyboardButton('Browse Authors',
                                         callback_data=BROWSE_AUTHORS), InlineKeyboardButton('Cancel', callback_data=CANCEL)
                ]]

    update.message.reply_text("Please choose an action: ",
                              reply_markup=InlineKeyboardMarkup(keyboard))

    return TYPE


def random(update: Update, context: CallbackContext):
    update.callback_query.answer()
    context.bot.send_chat_action(chat_id=update.effective_chat.id,
                                 action=ChatAction.TYPING)
    url = "https://poetrydb.org/random"
    response = {}
    while True:
        response = json.loads(
            requests.request("GET", url, headers=poetry_headers).text)[0]
        if int(response['linecount']) <= 17:
            break
    title = response['title']
    author = response['author']
    poem = "\n".join(response['lines'])

    sleep(5)
    update.callback_query.edit_message_text(title + "\n\n\n" + poem + "\n\n\n" +
                                            "- " + author)
    update.callback_query.answer()
    return ConversationHandler.END


def searchTitle(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_text("Enter keyword to search: ")


def searchAuthor(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_text("Enter keyword to search: ")


def browseAuthors(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_text("Enter keyword to search: ")


def cancel(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text("alright")
    return ConversationHandler.END


def main():
    updater = Updater(os.environ['token'], use_context=True)
    dp = updater.dispatcher

    convo_handler = ConversationHandler(
        entry_points=[(CommandHandler('start', start))],
        states={
            TYPE: [
                CallbackQueryHandler(random, pattern="^" + RANDOM + "$"),
                CallbackQueryHandler(searchTitle,
                                     pattern="^" + BY_TITLE + "$"),
                CallbackQueryHandler(searchAuthor,
                                     pattern="^" + BY_AUTHOR + "$"),
                CallbackQueryHandler(browseAuthors,
                                     pattern="^" + BROWSE_AUTHORS + "$"),
                CallbackQueryHandler(cancel, pattern="^" + CANCEL + "$")
            ]
        },
        fallbacks=[CommandHandler('Cancel', cancel)])

    
    dp.add_handler(convo_handler)
    updater.start_polling()


if __name__ == "__main__":
    main()
