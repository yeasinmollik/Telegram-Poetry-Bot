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
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton,
                      ReplyKeyboardRemove)
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

First_STEP, GET_ALL_TITLES, GET_SPECIFIC_TITLE, LIST_AUTHORS, POEMS_BY_AN_AUTHOR = range(5)

# url and headers for PoetryDB api
poetry_url = p_url
poetry_headers = p_headers


def start(update: Update, context: CallbackContext):
    keyboard = [['Random Poem'], ['Search by Title'], ['Browse by Authors'], ['Exit']]

    update.message.reply_text("*Choose any action: *",
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True,
                                                               input_field_placeholder='Actions: '),
                              parse_mode="MarkdownV2")

    return First_STEP


def randomPoem(update: Update, context: CallbackContext):
    context.bot.send_chat_action(chat_id=update.effective_chat.id,
                                 action=ChatAction.TYPING)

    url = "https://poetrydb.org/random"
    response = {}
    while True:
        response = json.loads(
            requests.request("GET", url, headers=poetry_headers).text)[0]
        if "Sonnet" not in response['title'] and int(response['linecount']) <= 30:
            break

    poem = ""
    for line in response['lines']:
        poem += backslash(line)

    poem = bold(backslash(response['title'])) + "\n\-" + italic(backslash(
        response['author'])) + "\n\n" + poem
    update.message.reply_text(poem[0:4096], parse_mode="MarkdownV2", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def searchTitle(update: Update, context: CallbackContext):
    update.message.reply_text("Type any keyword to search: ", reply_markup=ReplyKeyboardRemove())
    return GET_ALL_TITLES


def browseAuthors(update: Update, context: CallbackContext):
    keyboard = [[]]
    for i in range(0, 6):
        keyboard.append([InlineKeyboardButton(authors[i], callback_data=authors[i])])
        if len(keyboard) > 6:
            break

    keyboard.append([InlineKeyboardButton("Next..", callback_data="next")])
    update.callback_query.edit_message_text(text="Please choose a author: ",
                                            reply_markup=InlineKeyboardMarkup(keyboard))
    return LIST_AUTHORS


def exit(update: Update, context: CallbackContext):
    update.message.reply_text("Alright!", reply_markup=ReplyKeyboardRemove)
    return ConversationHandler.END


def getAllTitles(update: Update, context: CallbackContext):
    title = update.message.text
    url = "https://poetrydb.org/title/" + "title"
    # gets list of poems using api
    response = json.loads(requests.request("GET", url).text)
    if type(response) is dict:
        update.message.reply_text("No match found! Please /start to search again!")
        return ConversationHandler.END

    maxTitleLen = 0

    keyboard = [[]]
    for i in range(0, len(response)):
        keyboard.append([response[i]['title']])
    update.message.reply_text(text="*Choose your title:*",
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True,
                                                               input_field_placeholder="Matched poems"),
                              parse_mode="MarkdownV2")
    return GET_SPECIFIC_TITLE


def getAPoemByTitle(update: Update, context: CallbackContext):
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    title = update.message.text

    # gets list of poems using api
    response = json.loads(
        requests.request("GET", poetry_url + "/title/" + title, headers=poetry_headers).text)

    # since multiple poems having same keyword are returned, select one poem randomly from them

    poem = bold("\t" + backslash(response[0]['title'])) + "\n\- " + italic(backslash(
        response[0]['author'])) + "\n\n" + backslash("\n".join(
        response[0]['lines']))
    update.message.reply_text(poem[0:4096], parse_mode="MarkdownV2", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def listAuthors(update: Update, context: CallbackContext):
    keyboard = [[]]
    for author in authors:
        keyboard.append([author])
    update.message.reply_text("*Choose an author: *",
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True,
                                                               input_field_placeholder='Authors'),
                              parse_mode="MarkdownV2")
    return POEMS_BY_AN_AUTHOR


def poemsByAnAuthor(update: Update, context: CallbackContext):
    author = update.message.text
    url = "https://poetrydb.org/author/" + author + "/title"
    titles = json.loads(requests.request("GET", url).text)
    keyboard = [[]]
    for i in range(0, len(titles)):
        keyboard.append([titles[i]['title']])

    update.message.reply_text("*Choose any poem: *",
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True,
                                                               input_field_placeholder=author + "'s Poems"),
                              parse_mode="MarkdownV2")
    return GET_SPECIFIC_TITLE


def main():
    updater = Updater(os.environ['token'], use_context=True)
    dp = updater.dispatcher

    convo_handler = ConversationHandler(
        entry_points=[(CommandHandler('start', start))],

        states={
            First_STEP: [
                MessageHandler(Filters.text('Random Poem'), randomPoem),
                MessageHandler(Filters.text('Search by Title'), searchTitle),
                MessageHandler(Filters.text("Browse by Authors"), listAuthors),
                MessageHandler(Filters.text('Exit'), exit),
            ],
            GET_ALL_TITLES: [MessageHandler(Filters.text & ~Filters.command, getAllTitles)],
            GET_SPECIFIC_TITLE: [MessageHandler(Filters.text & ~Filters.command, getAPoemByTitle)],
            POEMS_BY_AN_AUTHOR: [MessageHandler(Filters.text & ~Filters.command, poemsByAnAuthor)]
        },

        fallbacks=[CommandHandler('Exit', exit)]
    )

    dp.add_handler(convo_handler)
    updater.start_polling()


if __name__ == "__main__":
    main()
