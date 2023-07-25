import os
from telebot import TeleBot

API_KEY = os.getenv('API_KEY')
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def greet(m):
    bot.send_message(m.chat.id, 'Hey there')


bot.infinity_polling()