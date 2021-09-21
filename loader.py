import telebot
from dotenv import load_dotenv
import os


load_dotenv()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

markup = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
button_lowprice = telebot.types.KeyboardButton('Найти дешевые')
button_highprice = telebot.types.KeyboardButton('Найти дорогие')
button_bestdeals = telebot.types.KeyboardButton('Лучшие предложения')
button_history = telebot.types.KeyboardButton('История поиска')
button_help = telebot.types.KeyboardButton('Помощь')
markup.add(button_lowprice, button_highprice, button_bestdeals, button_history, button_help)

help_text = 'Нажми на одну из кнопок или используй одну из следующих команд:\n\n' \
            '/lowprice или кнопка "Найти дешевые" — вывод самых дешёвых отелей в городе,\n' \
            '/highprice или кнопка "Найти дорогие" — вывод самых дорогих отелей в городе,\n' \
            '/bestdeal или кнопка "Лучшие предложения" — вывод отелей, наиболее подходящих по цене' \
                ' и расположению от центра,\n' \
            '/history или кнопка "История поиска" — вывод истории поиска отелей\n' \
            '/help или кнопка "Помощь" — помощь по командам бота.'
