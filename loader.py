import telebot
from dotenv import load_dotenv
import os
from requestapi import RapidApi
from loguru import logger
from telebot_calendar import Calendar, RUSSIAN_LANGUAGE, CallbackData
import datetime


logger.add('debug.log', format='{time} {level} {message}', level='DEBUG')
load_dotenv()
rapidapi_key = os.getenv('RAPIDAPI_KEY')

now = datetime.datetime.now()

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData('calendar_1', 'action', 'year', 'month', 'day')
calendar_2_callback = CallbackData('calendar_2', 'action', 'year', 'month', 'day')

markup = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
markup_next = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

button_lowprice = telebot.types.KeyboardButton('Найти дешевые')
button_highprice = telebot.types.KeyboardButton('Найти дорогие')
button_bestdeals = telebot.types.KeyboardButton('Лучшие предложения')
button_history = telebot.types.KeyboardButton('История поиска')
button_help = telebot.types.KeyboardButton('Помощь')
markup.add(button_lowprice, button_highprice, button_bestdeals, button_history, button_help)

button_next = telebot.types.KeyboardButton('Ок')
markup_next.add(button_next)

rapidapi = RapidApi(api_key=rapidapi_key)

help_text = 'Нажми на одну из кнопок или используй одну из следующих команд:\n\n' \
            '/lowprice или кнопка "Найти дешевые" — вывод самых дешёвых отелей в городе,\n' \
            '/highprice или кнопка "Найти дорогие" — вывод самых дорогих отелей в городе,\n' \
            '/bestdeal или кнопка "Лучшие предложения" — вывод отелей, наиболее подходящих по цене' \
                ' и расположению от центра,\n' \
            '/history или кнопка "История поиска" — вывод истории поиска отелей\n' \
            '/help или кнопка "Помощь" — помощь по командам бота.'
