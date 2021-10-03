from loader import bot
from loader import markup, markup_next
from loader import help_text
from handler import save_info_in_file
from loader import rapidapi
from loader import calendar, calendar_1_callback, calendar_2_callback
from loader import now
from telebot.types import CallbackQuery, ReplyKeyboardRemove


global hotels


@bot.message_handler(content_types=['text'])
def get_text_message(message: 'Message') -> None:
    """Функция для получения текстовых сообщений из telegram-бота.
    Объявляется слушатель для текстовых сообщений и их обработчик
    """

    if message.text.lower() == 'привет' or message.text.lower() == '/start':
        bot.send_message(message.from_user.id, 'Привет. Я помогу найти лучший отель в твоем городе', reply_markup=markup)
    elif message.text == 'Найти дешевые' or message.text == '/lowprice':
        bot.send_message(message.from_user.id, 'Сколько отелей показывать? (не более 15)', reply_markup=ReplyKeyboardRemove())
        hotels[message.from_user.id] = {'command': 'low'}
        bot.register_next_step_handler(message, set_max_size)
        save_info_in_file(message.from_user.id, '/lowprice')
    elif message.text == 'Найти дорогие' or message.text == '/highprice':
        hotels[message.from_user.id]['command'] = 'high'
        save_info_in_file(message.from_user.id, '/highprice')
    elif message.text == 'Лучшие предложения' or message.text == '/bestdeal':
        hotels[message.from_user.id]['command'] = 'best'
        save_info_in_file(message.from_user.id, '/bestdeal')
    elif message.text == 'Помощь' or message.text == '/help':
        bot.send_message(message.from_user.id, help_text, reply_markup=markup)
    elif message.text == 'История поиска' or message.text == '/history':
        bot.send_message(message.from_user.id, 'История поиска отелей:')
    else:
        bot.send_message(message.from_user.id, 'Я не понимаю такую команду. Напиши /help', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1_callback.prefix))
def callback_inline(call: 'CallbackQuery') -> None:
    """Функция, обрабатывает ответ от календаря"""

    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)
    if action == 'DAY':
        msg = bot.send_message(call.from_user.id,
                         f'Выбрана дата: {date.strftime("%d.%m.%Y")}',
                         reply_markup=markup_next)
        hotels[call.from_user.id]['date_in'] = date.strftime("%Y-%m-%d")
        bot.register_next_step_handler(msg, choose_date_out)
    elif action == 'CANCEL':
        bot.send_message(call.from_user.id,
                         'Отмена выбора даты',
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_2_callback.prefix))
def callback_inline(call: 'CallbackQuery') -> None:
    """Функция, обрабатывает ответ от календаря"""

    name, action, year, month, day = call.data.split(calendar_2_callback.sep)
    date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)
    if action == 'DAY':
        msg = bot.send_message(call.from_user.id,
                                f'Выбрана дата: {date.strftime("%d.%m.%Y")}',
                                reply_markup=markup_next)
        hotels[call.from_user.id]['date_out'] = date.strftime("%Y-%m-%d")
        bot.register_next_step_handler(msg, find_hotel)
    elif action == 'CANCEL':
        bot.send_message(call.from_user.id,
                         'Отмена.Продолжить?',
                         reply_markup=markup)


def set_max_size(message):
    """Функция, запрашивает количество отелей для показа"""

    if not message.text.isdigit():
        bot.send_message(message.from_user.id, 'Ошибка. Повторите ввод', reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, set_max_size)
    else:
        hotels[message.from_user.id]['max_size'] = message.text
        bot.send_message(message.from_user.id, 'В каком городе искать отели?')
        bot.register_next_step_handler(message, find_location)


def find_location(message: 'Message') -> None:
    """Функция, запрашивает локацию для поиска"""

    city = message.text
    hotels[message.from_user.id]['city'] = city
    destination = rapidapi.rapidapi_search(city)
    hotels[message.from_user.id]['locations_list'] = destination
    for elem in destination.keys():
        bot.send_message(message.from_user.id, elem)
    bot.send_message(message.from_user.id, 'В какой локации из списка искать отели?')
    bot.register_next_step_handler(message, choose_date_in)


def choose_date_in(message: 'Message') -> None:
    """Функция, запрашивает дату заезда в отель"""

    location = message.text
    hotels[message.from_user.id]['location'] = location
    if location not in hotels[message.from_user.id]['locations_list'].keys():
        bot.send_message(message.from_user.id, 'Ошибка! Повтори ввод')
        bot.register_next_step_handler(message, choose_date_in)
        return
    bot.send_message(
        message.from_user.id,
        'Какая дата заезда?',
        reply_markup=calendar.create_calendar(
            name=calendar_1_callback.prefix,
            year=now.year,
            month=now.month
        )
    )


def choose_date_out(message: 'Message') -> None:
    """Функция, запрашивает дату выезда из отеля"""

    bot.send_message(
        message.from_user.id,
        'Какая дата выезда?',
        reply_markup=calendar.create_calendar(
            name=calendar_2_callback.prefix,
            year=now.year,
            month=now.month
        )
    )


def find_hotel(message: 'Message') -> None:
    """Функция, ищет отели и выводит результат поиска в Телеграмм-боте"""

    location = hotels[message.from_user.id]['location']
    command = hotels[message.from_user.id]['command']
    destination_id = hotels[message.from_user.id]['locations_list'][location]
    max_size_page = int(hotels[message.from_user.id]['max_size'])
    date_in = hotels[message.from_user.id]['date_in']
    date_out = hotels[message.from_user.id]['date_out']
    bot.send_message(message.from_user.id, 'Ищу варианты', reply_markup=ReplyKeyboardRemove())
    hotels[message.from_user.id]['hotels'] = rapidapi.hotel_info(destination_id, command, max_size_page, date_in, date_out)
    i = 1
    for elem in hotels[message.from_user.id]['hotels']:
        bot.send_message(message.from_user.id, i)
        bot.send_message(message.from_user.id, ': '.join(('Отель', elem.name)))
        bot.send_message(message.from_user.id, ': '.join(('Адрес', elem.address)))
        bot.send_message(message.from_user.id, ': '.join(('Стоимость за все время', elem.price)))
        bot.send_message(message.from_user.id, ': '.join(('Удаленность от центра', elem.distance)))
        i += 1
    bot.send_message(message.from_user.id, 'Продолжить?', reply_markup=markup)


if __name__ == '__main__':
    hotels = dict()
    bot.polling(none_stop=True, interval=0)
