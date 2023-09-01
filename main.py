import os
import schedule
import time
import db
import exchange as ex
from threading import Thread
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
import bot_messages as messages
from telebot.formatting import escape_markdown

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = TeleBot(BOT_TOKEN)

buttons = {
    'create': 'Create an alert',
    'view_all': 'View my alerts',
    'remove_one': 'Remove an alert',
    'remove_all': 'Remove all alerts'
}


@bot.message_handler(commands=['start'])
def greet(m):
    if user_exists(m.chat.id):
        markup = get_menu_markup()
        alerts = db.read_all(m.chat.id)
        for a in alerts:
            run_scheduled_task(a[3], a[1], a[5], a[2], a[4])
    else:
        db.save_user(m.chat.id)
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton(buttons.get('create')))
    bot.send_message(m.chat.id, messages.GREETING, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == buttons.get('create'))
def alert(m):
    rm = ReplyKeyboardRemove()  # remove custom keyboard
    bot.send_message(m.chat.id, messages.PROVIDE_ABBR, reply_markup=rm)
    bot.register_next_step_handler(m, get_crypto_abbr)


def get_crypto_abbr(m):
    crypto_abbr = str.upper(m.text)
    if not ex.is_currency_supported(crypto_abbr):
        markup = get_menu_markup()
        bot.send_message(m.chat.id, messages.NO_SUCH_CURRENCY, reply_markup=markup)
    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton(messages.ABOVE))
        markup.add(KeyboardButton(messages.BELOW))
        bot.send_message(m.chat.id, messages.SPECIFY_OPTION, reply_markup=markup)
        bot.register_next_step_handler(m, get_option, crypto_abbr)


def get_option(m, crypto_abbr):
    option = m.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(messages.DOLLAR))
    markup.add(KeyboardButton(messages.PERCENT))
    bot.send_message(m.chat.id, messages.SPECIFY_PRICE_OR_PERCENT, reply_markup=markup)
    bot.register_next_step_handler(m, price_or_percent_handler, crypto_abbr, option)


def price_or_percent_handler(m, crypto_abbr, option):
    user_selection = m.text
    match user_selection:
        case messages.DOLLAR: ask_for_price(m, crypto_abbr, option)
        case messages.PERCENT: ask_for_percent(m, crypto_abbr, option)


def ask_for_price(m, crypto_abbr, option):
    rm = ReplyKeyboardRemove()
    bot.send_message(m.chat.id, messages.PROVIDE_PRICE, reply_markup=rm)
    bot.register_next_step_handler(m, get_price, crypto_abbr, option)


def ask_for_percent(m, crypto_abbr, option):
    rm = ReplyKeyboardRemove()
    avg_price = ex.get_avg_price(crypto_abbr)
    bot.send_message(m.chat.id,
                     f'Provide a percentage of the current average price. It is {avg_price} now.',
                     reply_markup=rm)
    bot.register_next_step_handler(m, get_percent, crypto_abbr, option)


def get_percent(m, crypto_abbr, option):
    rm = ReplyKeyboardRemove()
    percent = float(m.text)
    avg_price = ex.get_avg_price(crypto_abbr)
    price = calculate_price(avg_price, percent, option)
    bot.send_message(m.chat.id, f'Ok, I will send you a message when the price will reach {price}')
    bot.send_message(m.chat.id, messages.SPECIFY_DELAY, reply_markup=rm)
    bot.register_next_step_handler(m, get_price_check_delay, crypto_abbr, option, price)


def calculate_price(avg_price, percent, option):
    price = None
    match option:
        case messages.ABOVE: price = avg_price + percent * avg_price / 100
        case messages.BELOW: price = avg_price - percent * avg_price / 100
    return price


def get_price(m, crypto_abbr, option):
    price = float(m.text)
    bot.send_message(m.chat.id, messages.SPECIFY_DELAY)
    bot.register_next_step_handler(m, get_price_check_delay, crypto_abbr, option, price)


def get_price_check_delay(m, crypto_abbr, option, price):
    menu = get_menu_markup()
    delay = int(m.text)
    bot.send_message(m.chat.id, f'You will be notified as soon as the price goes {option} the target price.',
                     reply_markup=menu)
    db.save_alert(m.chat.id, crypto_abbr, option, price, delay)
    run_scheduled_task(m.chat.id, crypto_abbr, option, price, delay)


def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)


def run_scheduled_task(chat_id, crypto_abbr, option, price, delay):
    (schedule.every(delay)
     .minutes.do(compare_prices, chat_id=chat_id, crypto_abbr=crypto_abbr, option=option, price=price))


def compare_prices(chat_id, crypto_abbr, option, price):
    avg_price = float(ex.get_avg_price(crypto_abbr))
    if option == messages.ABOVE:
        if avg_price > price:
            bot.send_message(chat_id,
                             f'The price of {crypto_abbr} has gone up. It\'s now at {avg_price:.3f}')
    elif option == messages.BELOW:
        if avg_price < price:
            bot.send_message(chat_id,
                             f'The price of {crypto_abbr} has dropped. It\'s now at {avg_price:.3f}')


@bot.message_handler(func=lambda message: message.text == buttons.get('view_all'))
def view_alerts(m):
    alerts = db.read_all(m.chat.id)
    if len(alerts) == 0:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton(buttons.get('create')))
        bot.send_message(m.chat.id, messages.NO_ALERTS, reply_markup=markup)
    else:
        for a in alerts:
            message = (f'Alert№`{a[0]}`\n\nA notification will be sent as soon as {a[1]} goes '
                       f'{a[5]} the price of {a[2]}$.\n'
                       f'Checking will occur every ')
            if a[4] == 1:
                message += 'minute.'
            else:
                message += f'{a[4]} minutes.'
            message = escape_markdown(message).replace('\\', '', 2)
            bot.send_message(m.chat.id, message, parse_mode='MarkdownV2')


@bot.message_handler(func=lambda message: message.text == buttons.get('remove_all'))
def remove_all_alerts(m):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(messages.YES))
    markup.add(KeyboardButton(messages.NO))
    bot.send_message(m.chat.id, messages.CONFIRM_TO_REMOVE, reply_markup=markup)
    bot.register_next_step_handler(m, handle_yes_no_answers,
                                   confirm_all_alerts_deletion, deny_all_alerts_deletion)


def handle_yes_no_answers(m, confirm_callback, deny_callback):
    match m.text:
        case messages.YES:
            confirm_callback(m.chat.id)
        case messages.NO:
            deny_callback(m.chat.id)


def confirm_all_alerts_deletion(tg_id):
    db.remove_all(tg_id)
    menu = get_menu_markup()
    bot.send_message(tg_id, messages.ALERTS_HAVE_BEEN_DELETED, reply_markup=menu)


def deny_all_alerts_deletion(tg_id):
    menu = get_menu_markup()
    bot.send_message(tg_id, messages.OK, reply_markup=menu)


def get_menu_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(buttons.get('create')))
    markup.add(KeyboardButton(buttons.get('view_all')))
    markup.add(KeyboardButton(buttons.get('remove_one')))
    markup.add(KeyboardButton(buttons.get('remove_all')))
    return markup


@bot.message_handler(func=lambda message: message.text == buttons.get('remove_one'))
def remove_alert_by_id(m):
    bot.send_message(m.chat.id, messages.PROVIDE_ALERT_ID)
    bot.register_next_step_handler(m, handle_alert_id)


def handle_alert_id(m):
    alert_id = m.text
    if alert_exists(alert_id) and user_has_alert(m.chat.id, alert_id):
        db.remove_by_id(alert_id)
        bot.send_message(m.chat.id, f'The alert with id {alert_id} has been deleted successfully.')
    else:
        bot.send_message(m.chat.id, messages.NO_ALERTS_WITH_SUCH_ID)


def alert_exists(alert_id):
    exists = False
    if len(db.get_alert_by_id(alert_id)) != 0:
        exists = True
    return exists


def user_has_alert(user_id, alert_id):
    has = False
    if len(db.get_alert_by_user_id_and_alert_id(user_id, alert_id)) != 0:
        has = True
    return has


def user_exists(user_id):
    exists = False
    if db.get_user_by_id(user_id) is not None:
        exists = True
    return exists


@bot.message_handler(func=lambda message: True)
def handle_other_messages(m):
    menu = get_menu_markup()
    bot.send_message(m.chat.id, messages.NO_SUCH_COMMAND, reply_markup=menu)


if __name__ == '__main__':
    Thread(target=schedule_checker).start()

bot.infinity_polling()