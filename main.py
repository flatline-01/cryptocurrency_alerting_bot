import os
import schedule
import time
import db
from threading import Thread
from binance.spot import Spot
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = TeleBot(BOT_TOKEN)
client = Spot(api_key=API_KEY, api_secret=API_SECRET)

buttons = {
    'create': 'Create an alert',
    'view_all': 'View my alerts',
    'remove_all': 'Remove all alerts'
}


@bot.message_handler(commands=['start'])
def greet(m):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(buttons.get('create')))
    bot.send_message(m.chat.id, 'Hey there', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == buttons.get('create'))
def alert(m):
    rm = ReplyKeyboardRemove()  # remove custom keyboard
    bot.send_message(m.chat.id, 'Provide a cryptocurrency abbreviation:', reply_markup=rm)
    bot.register_next_step_handler(m, get_crypto_abbr)


def get_crypto_abbr(m):
    crypto_abbr = str.upper(m.text)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('above'))
    markup.add(KeyboardButton('below'))
    bot.send_message(m.chat.id,
                     'Do you want to get notified when a coin goes above or below a price target?',
                     reply_markup=markup)
    bot.register_next_step_handler(m, get_option, crypto_abbr)


def get_option(m, crypto_abbr):
    rm = ReplyKeyboardRemove()
    option = m.text
    bot.send_message(m.chat.id,
                     'Provide the dollar price of the cryptocurrency, after which the notification should be sent: ',
                     reply_markup=rm)
    bot.register_next_step_handler(m, get_price, crypto_abbr, option)


def get_price(m, crypto_abbr, option):
    price = float(m.text)
    bot.send_message(m.chat.id, 'How often should I check the price? Specify the delay in minutes.')
    bot.register_next_step_handler(m, get_price_check_delay, crypto_abbr, option, price)


def get_price_check_delay(m, crypto_abbr, option, price):
    menu = get_menu_markup()
    delay = int(m.text)
    bot.send_message(m.chat.id, f'You will be notified as soon as the price goes {option} the target price.',
                     reply_markup=menu)
    run_scheduled_task(m.chat.id, crypto_abbr, option, price, delay)


def run_scheduled_task(chat_id, crypto_abbr, option, price, delay):
    db.save_alert(chat_id, crypto_abbr, option, price, delay)
    (schedule.every(delay)
     .minutes.do(compare_prices, chat_id=chat_id, crypto_abbr=crypto_abbr, option=option, price=price))
    Thread(target=schedule_checker).start()


def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)


def compare_prices(chat_id, crypto_abbr, option, price):
    avg_price = float(get_avg_price(crypto_abbr))
    if option == 'above':
        if avg_price > price:
            bot.send_message(chat_id,
                             f'The price of {crypto_abbr} has gone up. It\'s now at {avg_price:.3f}')
    elif option == 'below':
        if avg_price < price:
            bot.send_message(chat_id,
                             f'The price of {crypto_abbr} has dropped. It\'s now at {avg_price:.3f}')


def get_avg_price(currency):
    return float(client.avg_price(symbol=f'{currency}USDT')['price'])


@bot.message_handler(func=lambda message: message.text == buttons.get('view_all'))
def view_alerts(m):
    alerts = db.read_all(m.chat.id)
    i = 0
    if len(alerts) == 0:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton(buttons.get('create')))
        bot.send_message(m.chat.id, 'You don\'t have any alerts yet. Press the button to create a new alert.',
                         reply_markup=markup)
    else:
        for a in alerts:
            i += 1
            message = (f'Alert№{i}\n\nA notification will be sent as soon as {a[1]} goes {a[5]} the price of {a[2]}$.\n'
                       f'Checking will occur every ')
            if a[4] == 1:
                message += 'minute.'
            else:
                message += f'{a[4]} minutes.'
            bot.send_message(m.chat.id, message)


@bot.message_handler(func=lambda message: message.text == buttons.get('remove_all'))
def remove_all_alerts(m):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Yes'))
    markup.add(KeyboardButton('No'))
    bot.send_message(m.chat.id, 'Do you really want to remove all your alerts?', reply_markup=markup)
    bot.register_next_step_handler(m, handle_yes_no_answers,
                                   confirm_all_alerts_deletion, deny_all_alerts_deletion)


def handle_yes_no_answers(m, confirm_callback, deny_callback):
    match m.text:
        case 'Yes':
            confirm_callback(m.chat.id)
        case 'No':
            deny_callback(m.chat.id)


def confirm_all_alerts_deletion(tg_id):
    db.remove_all(tg_id)
    menu = get_menu_markup()
    bot.send_message(tg_id, 'Your alerts have just been deleted.', reply_markup=menu)


def deny_all_alerts_deletion(tg_id):
    menu = get_menu_markup()
    bot.send_message(tg_id, 'Ok', reply_markup=menu)


def get_menu_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(buttons.get('create')))
    markup.add(KeyboardButton(buttons.get('view_all')))
    markup.add(KeyboardButton(buttons.get('remove_all')))
    return markup


bot.infinity_polling()