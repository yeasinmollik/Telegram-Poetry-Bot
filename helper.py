import json
import logging
import os
import random
from time import sleep
from typing import List, Tuple, cast
from telegram.chataction import ChatAction
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler, CallbackContext, InvalidCallbackData,
                          PicklePersistence, MessageHandler, Filters, )

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

POEM, QUOTE, EXIT = "poem", "quote", "EXIT"


def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Poem", callback_data=POEM)],
                [InlineKeyboardButton("Quote", callback_data=QUOTE)],
                [InlineKeyboardButton("Exit", callback_data=EXIT)]]
    update.message.reply_text("Please choose: ", reply_markup=InlineKeyboardMarkup(keyboard))


def searchPoem(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_text("Please enter any keyboard to search: ")


# makes text bold for MarkdownV2
def bold(s):
    return "*" + s + "*"
def italic(s):
    return "_" + s + "_"

# add backslash before special chars because MarkdownV2 requires that
def backslash(s):
    l = [
        '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{',
        '}', '.', '!'
    ]
    for ch in l:
        s = s.replace(ch, "\{}".format(ch))
    return s


def returnPoem(update: Update, context: CallbackContext):
    # url and header for poetry api
    p_url = "https://thundercomb-poetry-db-v1.p.rapidapi.com/title/"
    p_headers = {
        "X-RapidAPI-Host": "thundercomb-poetry-db-v1.p.rapidapi.com",
        "X-RapidAPI-Key": "fa62bd94d0msh32c981feda8321bp15849djsne577d809c232"
    }

    title = update.message.text
    # get poems using api
    response = json.loads(
        requests.request("GET", p_url + title, headers=p_headers).text)
    if type(response) is dict:
        return backslash("No match found! Please /start again!")
    # pprint.pprint(response)

    # since multiple poems having same keyword are returned, select one poem randomly from them
    idx = random.randint(0, len(response) - 1)

    # below lines are to alight the title to the centre
    mxLength = len(max(response[idx]['lines'], key=len))
    titleLength = len(response[idx]['title'])
    title = ""
    if titleLength < mxLength:
        title = " " * int((mxLength + 1 - titleLength) / 2) + response[idx]['title']
    else:
        title = response[idx]['title']

    title = bold(backslash(title))
    # Joining lines of the same poem
    poem = ""
    for s in response[idx]['lines']:
        poem += backslash(s) + "\n"
    poem = title + "\n\n" + poem + "\n\n\- " + bold(response[idx]['author'])

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    sleep(1)
    update.message.reply_text(poem[0:4096], parse_mode="MarkdownV2")


def main():
    updater = Updater(os.environ['token'], use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(searchPoem, pattern="^" + POEM + "$"))
    dp.add_handler(MessageHandler(Filters.text, returnPoem))

    updater.start_polling()


#########################

p_url = "https://thundercomb-poetry-db-v1.p.rapidapi.com/"
p_headers = {
    "X-RapidAPI-Host": "thundercomb-poetry-db-v1.p.rapidapi.com",
    "X-RapidAPI-Key": "fa62bd94d0msh32c981feda8321bp15849djsne577d809c232"
}



authors = {
    'Adam Lindsay Gordon', 'Alan Seeger', 'Alexander Pope',
    'Algernon Charles Swinburne', 'Ambrose Bierce', 'Amy Levy',
    'Andrew Marvell', 'Ann Taylor', 'Anne Bradstreet', 'Anne Bronte',
    'Anne Killigrew', 'Anne Kingsmill Finch', 'Annie Louisa Walker',
    'Arthur Hugh Clough', 'Ben Jonson', 'Charles Kingsley', 'Charles Sorley',
    'Charlotte Bronte', 'Charlotte Smith', 'Christina Rossetti',
    'Christopher Marlowe', 'Christopher Smart', 'Coventry Patmore',
    'Edgar Allan Poe', 'Edmund Spenser', 'Edward Fitzgerald', 'Edward Lear',
    'Edward Taylor', 'Edward Thomas', 'Eliza Cook',
    'Elizabeth Barrett Browning', 'Emily Bronte', 'Emily Dickinson',
    'Emma Lazarus', 'Ernest Dowson', 'Eugene Field', 'Francis Thompson',
    'Geoffrey Chaucer', 'George Eliot', 'George Gordon, Lord Byron',
    'George Herbert', 'George Meredith', 'Gerard Manley Hopkins',
    'Helen Hunt Jackson', 'Henry David Thoreau', 'Henry Vaughan',
    'Henry Wadsworth Longfellow', 'Hugh Henry Brackenridge', 'Isaac Watts',
    'James Henry Leigh Hunt', 'James Thomson', 'James Whitcomb Riley',
    'Jane Austen', 'Jane Taylor', 'John Clare', 'John Donne', 'John Dryden',
    'John Greenleaf Whittier', 'John Keats', 'John McCrae', 'John Milton',
    'John Trumbull', 'John Wilmot', 'Jonathan Swift', 'Joseph Warton',
    'Joyce Kilmer', 'Julia Ward Howe', 'Jupiter Hammon', 'Katherine Philips',
    'Lady Mary Chudleigh', 'Lewis Carroll', 'Lord Alfred Tennyson',
    'Louisa May Alcott', 'Major Henry Livingston, Jr.', 'Mark Twain',
    'Mary Elizabeth Coleridge', 'Matthew Arnold', 'Matthew Prior',
    'Michael Drayton', 'Oliver Goldsmith', 'Oliver Wendell Holmes',
    'Oscar Wilde', 'Paul Laurence Dunbar', 'Percy Bysshe Shelley',
    'Philip Freneau', 'Phillis Wheatley', 'Ralph Waldo Emerson',
    'Richard Crashaw', 'Richard Lovelace', 'Robert Browning', 'Robert Burns',
    'Robert Herrick', 'Robert Louis Stevenson', 'Robert Southey', 'Robinson',
    'Rupert Brooke', 'Samuel Coleridge', 'Samuel Johnson',
    'Sarah Flower Adams', 'Sidney Lanier', 'Sir John Suckling',
    'Sir Philip Sidney', 'Sir Thomas Wyatt', 'Sir Walter Raleigh',
    'Sir Walter Scott', 'Stephen Crane', 'Thomas Campbell',
    'Thomas Chatterton', 'Thomas Flatman', 'Thomas Gray', 'Thomas Hood',
    'Thomas Moore', 'Thomas Warton', 'Walt Whitman', 'Walter Savage Landor',
    'Wilfred Owen', 'William Allingham', 'William Barnes', 'William Blake',
    'William Browne', 'William Cowper', 'William Cullen Bryant',
    'William Ernest Henley', 'William Lisle Bowles', 'William Morris',
    'William Shakespeare', 'William Topaz McGonagall', 'William Vaughn Moody',
    'William Wordsworth'
}

if __name__ == '__main__':
    main()
