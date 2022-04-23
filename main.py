from requests import request
from helper import authors, p_url, p_headers, bold, backslash, italic
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

First_STEP, SECOND_STEP = range(2)

# url and headers for PoetryDB api
poetry_url = p_url
poetry_headers = p_headers


def start(update: Update, context: CallbackContext):

    keyboard = [[InlineKeyboardButton('Random Poem', callback_data=RANDOM)],
                [
                    InlineKeyboardButton('Search by Title',
                                         callback_data=BY_TITLE),
                    InlineKeyboardButton('Search by Author',
                                         callback_data=BY_AUTHOR)
                ],
                [
                    InlineKeyboardButton('Browse Authors',
                                         callback_data=BROWSE_AUTHORS),
                    InlineKeyboardButton('Exit', callback_data=CANCEL)
                ]]

    update.message.reply_text("*Choose any action: *",
                              reply_markup=InlineKeyboardMarkup(keyboard),
                              parse_mode="MarkdownV2")
    #update.message.delete(update.message.message_id)

    return First_STEP


def randomPoem(update: Update, context: CallbackContext):
    update.callback_query.answer()
    context.bot.send_chat_action(chat_id=update.effective_chat.id,
                                 action=ChatAction.TYPING)
    url = "https://poetrydb.org/random"
    response = {}
    while True:
        response = json.loads(
            requests.request("GET", url, headers=poetry_headers).text)[0]
        if int(response['linecount']
               ) <= 17 and "Sonnet" not in response['title']:
            break
    poem = ""
    for line in response['lines']:
        poem += backslash(line)

    poem = bold(backslash(response['title'])) + "\n\n" + italic(backslash(
        response['author'])) + "\n\n" + poem
    sleep(1)

    update.callback_query.edit_message_text(poem, parse_mode="MarkdownV2")
    update.callback_query.answer()
    return ConversationHandler.END


def searchTitle(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_text("Enter keyword to search: ")
    return SECOND_STEP


def searchAuthor(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_text("Enter keyword to search: ")
    return


def browseAuthors(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_text("Enter keyword to search: ")


def cancel(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text("alright")
    return ConversationHandler.END


def getTitle(update: Update, context: CallbackContext):
    context.bot.send_chat_action(chat_id=update.effective_chat.id,
                                 action=ChatAction.TYPING)
    title = update.message.text

    # gets list of poems using api
    response = json.loads(
        requests.request("GET",
                         poetry_url + "/title/" + title,
                         headers=poetry_headers).text)
    if type(response) is dict:
        update.message.reply_text("No match found! Please /start again!")
        return ConversationHandler.END

    # since multiple poems having same keyword are returned, select one poem randomly from them
    idx = 0
    for i in range(0, len(response)):
        idx = random.randint(0, len(response) - 1)
        if int(response[idx]['linecount']) <= 20:
            break

    # poem = bold(
    #     backslash("      " + response[idx]['title'])) + "\n\n\n" + + "\n\n\- " + backslash(
    #             response[idx]['author'])
    poem = bold("\t"+backslash(response[idx]['title'])) + "\n\n\- " + italic(backslash(
        response[idx]['author'])) + "\n\n" + backslash("\n".join(
            response[idx]['lines']))

    sleep(1)
    update.message.reply_text(poem[0:4096], parse_mode="MarkdownV2")
    return ConversationHandler.END


def main():
    updater = Updater(os.environ['token'], use_context=True)
    dp = updater.dispatcher

    convo_handler = ConversationHandler(
        entry_points=[(CommandHandler('start', start))],
        states={
            First_STEP: [
                CallbackQueryHandler(randomPoem, pattern="^" + RANDOM + "$"),
                CallbackQueryHandler(searchTitle,
                                     pattern="^" + BY_TITLE + "$"),
                CallbackQueryHandler(searchAuthor,
                                     pattern="^" + BY_AUTHOR + "$"),
                CallbackQueryHandler(browseAuthors,
                                     pattern="^" + BROWSE_AUTHORS + "$"),
                CallbackQueryHandler(cancel, pattern="^" + CANCEL + "$")
            ],
            SECOND_STEP: [MessageHandler(Filters.text, getTitle)]
        },
        fallbacks=[CommandHandler('Cancel', cancel)])

    dp.add_handler(convo_handler)
    updater.start_polling()


if __name__ == "__main__":
    main()
