import os
import schedule
import time
from threading import Thread
from binance.spot import Spot
from telebot import TeleBot

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
BOT_TOKEN = os.getenv('BOT_TOKEN')
PRICE_CHECK_DELAY = 30

bot = TeleBot(BOT_TOKEN)
client = Spot(api_key=API_KEY, api_secret=API_SECRET)


@bot.message_handler(commands=['start'])
def greet(m):
    bot.send_message(m.chat.id, 'Hey there')


@bot.message_handler(commands=['alert'])
def alert(m):
    bot.send_message(m.chat.id, 'Provide a crypto code:')
    bot.register_next_step_handler(m, get_crypto_abbr)


def get_crypto_abbr(m):
    crypto_abbr = m.text
    bot.send_message(m.chat.id,
                     'Provide the price of the cryptocurrency, after which the notification should be sent: ')
    bot.register_next_step_handler(m, get_price, crypto_abbr)


def get_price(m, crypto_abbr):
    price = float(m.text)
    bot.send_message(m.chat.id, 'You will be notified as soon as the price goes up.')
    run_scheduled_task(m.chat.id, crypto_abbr, price)


def run_scheduled_task(chat_id, crypto_abbr, price):
    (schedule.every(PRICE_CHECK_DELAY)
     .minutes.do(compare_prices, chat_id=chat_id, crypto_abbr=crypto_abbr, price=price))
    Thread(target=schedule_checker).start()


def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)


def compare_prices(chat_id, crypto_abbr, price):
    avg_price = float(get_avg_price(crypto_abbr))
    if avg_price >= price:
        bot.send_message(chat_id,
                         f'The price of {crypto_abbr} has gone up. It\'s now at {avg_price:.3f}')


def get_avg_price(currency):
    return float(client.avg_price(symbol=f'{str.upper(currency)}USDT')['price'])


bot.infinity_polling()