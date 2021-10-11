from loader import bot
from loader import markup, markup_next, markup_retry
from loader import help_text
from handler import save_info_in_db, load_info_db
from loader import rapidapi
from loader import calendar, calendar_1_callback, calendar_2_callback
from loader import now
from telebot.types import CallbackQuery, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telebot.apihelper import ApiTelegramException


global hotels


@bot.message_handler(content_types=['text'])
def get_text_message(message: 'Message') -> None:
    """Функция для получения текстовых сообщений из telegram-бота.
    Объявляется слушатель для текстовых сообщений и их обработчик
    """

    if message.text.lower() == 'привет' or message.text.lower() == '/start':
        bot.send_message(message.from_user.id, 'Привет! Я помогу найти лучший отель в твоем городе', reply_markup=markup)
    elif message.text == 'Выполнить':
        bot.send_message(message.from_user.id, 'Что нужно сделать? Выберите команду', reply_markup=markup)
    elif message.text == 'Найти дешевые' or message.text == '/lowprice':
        bot.send_message(message.from_user.id, 'Сколько отелей показывать? (не более 15)',
                         reply_markup=ReplyKeyboardRemove())
        hotels[message.from_user.id] = {'command': 'lowprice'}
        bot.register_next_step_handler(message, set_max_size)
    elif message.text == 'Найти дорогие' or message.text == '/highprice':
        bot.send_message(message.from_user.id, 'Сколько отелей показывать? (не более 15)',
                         reply_markup=ReplyKeyboardRemove())
        hotels[message.from_user.id] = {'command': 'highprice'}
        bot.register_next_step_handler(message, set_max_size)
    elif message.text == 'Лучшие предложения' or message.text == '/bestdeal':
        bot.send_message(message.from_user.id, 'Сколько отелей показывать? (не более 15)',
                         reply_markup=ReplyKeyboardRemove())
        hotels[message.from_user.id] = {'command': 'bestdeal'}
        bot.register_next_step_handler(message, set_max_size)
    elif message.text == 'Помощь' or message.text == '/help':
        bot.send_message(message.from_user.id, help_text, reply_markup=markup)
    elif message.text == 'История поиска' or message.text == '/history':
        bot.send_message(message.from_user.id, 'История поиска отелей:')
        res_list = load_info_db(message.from_user.id)

        if res_list is None or len(res_list) == 0:
            bot.send_message(message.from_user.id, 'Нет истории запросов. Выполнить другой запрос?',
                             reply_markup=markup_retry)
            return
        bot.send_message(message.from_user.id, 'Будут показаны последние 10 запросов',
                         reply_markup=ReplyKeyboardRemove())
        for elem in res_list:
            text = "\n".join((': '.join(('Дата и время запроса', elem[1])),
                              ': '.join(('Город поиска', elem[2])),
                              ': '.join(('Локация города', elem[3])),
                              ': '.join(('Команда запроса', elem[4], '\n')),
                              ':'.join(('Найденные отели', elem[5]))))
            bot.send_message(message.from_user.id, text)
        bot.send_message(message.from_user.id, 'Выполнить другой запрос?', reply_markup=markup_retry)
    else:
        bot.send_message(message.from_user.id, 'Я не понимаю такую команду. Используй кнопку Помощь или команду /help',
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1_callback.prefix))
def callback_inline(call: 'CallbackQuery') -> None:
    """Функция, обрабатывает ответ от календаря"""

    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)
    if action == 'DAY':
        msg = bot.send_message(call.from_user.id, f'Выбрана дата: {date.strftime("%d.%m.%Y")}',
                               reply_markup=markup_next)
        hotels[call.from_user.id]['date_in'] = date.strftime("%Y-%m-%d")
        bot.register_next_step_handler(msg, choose_date_out)
    elif action == 'CANCEL':
        bot.send_message(call.from_user.id,
                         'Отмена выбора даты. Выполнить другой запрос??',
                         reply_markup=markup_retry)


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_2_callback.prefix))
def callback_inline(call: 'CallbackQuery') -> None:
    """Функция, обрабатывает ответ от календаря"""

    name, action, year, month, day = call.data.split(calendar_2_callback.sep)
    date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)
    if action == 'DAY':
        bot.send_message(call.from_user.id,
                         f'Выбрана дата: {date.strftime("%d.%m.%Y")}',
                         reply_markup=ReplyKeyboardRemove())
        hotels[call.from_user.id]['date_out'] = date.strftime("%Y-%m-%d")

        markup_photos = InlineKeyboardMarkup()
        yes_button = InlineKeyboardButton(text='Да', callback_data='yes')
        no_button = InlineKeyboardButton(text='Нет', callback_data='no')
        markup_photos.add(yes_button)
        markup_photos.add(no_button)
        bot.send_message(call.from_user.id, 'Показывать фото отелей?', reply_markup=markup_photos)
    elif action == 'CANCEL':
        bot.send_message(call.from_user.id,
                         'Отмена. Повторить запрос?',
                         reply_markup=markup_retry)


@bot.callback_query_handler(func=lambda call: call.data == 'yes' or call.data == 'no')
def show_photos(call: 'CallbackQuery') -> None:
    """Функция, запрашивает пользователя показывать ли фото отелей"""

    if call.data == 'yes':
        msg = bot.send_message(call.from_user.id,
                               'Сколько фотографий показывать? (не более 30)',
                               reply_markup=ReplyKeyboardRemove())
        hotels[call.from_user.id]['show_photo'] = 'yes'
        bot.register_next_step_handler(msg, set_max_photos)
    elif call.data == 'no':
        msg = bot.send_message(call.from_user.id, 'Без фото', reply_markup=markup_next)
        hotels[call.from_user.id]['show_photo'] = 'no'
        if hotels[call.from_user.id]['command'] == 'bestdeal':
            msg = bot.send_message(call.from_user.id, 'Какая максимальная стоимость для выбора отелей? (в рублях)',
                                   reply_markup=ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, choose_max_price)
        else:
            bot.register_next_step_handler(msg, find_hotel)


@bot.callback_query_handler(func=lambda call: call.data in hotels[call.from_user.id]['locations_list'].keys())
def callback_location(call: 'CallbackQuery'):
    """Функция, запоминает локацию"""

    hotels[call.from_user.id]['location'] = call.data
    msg = bot.send_message(call.from_user.id, f'Выбрана локация: {call.data}', reply_markup=markup_next)
    bot.register_next_step_handler(msg, choose_date_in)


def set_max_photos(message: 'Message') -> None:
    """Функция, запрашивает количество фото для показа"""

    if not message.text.isdigit():
        bot.send_message(message.from_user.id, 'Ошибка. Повторите ввод', reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, set_max_photos)
    else:
        hotels[message.from_user.id]['max_photos'] = message.text
        bot.send_message(message.from_user.id, f'Будут показаны по {message.text} фото', reply_markup=markup_next)
        if hotels[message.from_user.id]['command'] == 'bestdeal':
            bot.send_message(message.from_user.id, 'Какая максимальная стоимость для выбора отелей? (в рублях)',
                             reply_markup=ReplyKeyboardRemove())
            bot.register_next_step_handler(message, choose_max_price)
        else:
            bot.register_next_step_handler(message, find_hotel)


def choose_max_price(message: 'Message') -> None:
    """Функция, устанавливает максимальную стоимость отелей для показа"""

    if not message.text.isdigit():
        bot.send_message(message.from_user.id, 'Ошибка. Повторите ввод', reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, choose_max_price)
    else:
        hotels[message.from_user.id]['max_price'] = message.text
        bot.send_message(message.from_user.id, 'На каком максимальном расстояние от центра искать отели (в км.)?',
                         reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, choose_max_distance)


def choose_max_distance(message: 'Message') -> None:
    """Функция, устанавливает максимальное расстояние от центра для поиска"""

    if not message.text.isdigit():
        bot.send_message(message.from_user.id, 'Ошибка. Повторите ввод', reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, choose_max_distance)
    else:
        hotels[message.from_user.id]['max_distance'] = message.text
        bot.send_message(message.from_user.id,
                         f'Ищу отели не дороже {hotels[message.from_user.id]["max_price"]} руб.'
                         f' не далее чем {message.text} км. от центра', reply_markup=markup_next)
        bot.register_next_step_handler(message, find_hotel)


def set_max_size(message: 'Message') -> None:
    """Функция, запрашивает количество отелей для показа"""

    if not message.text.isdigit():
        bot.send_message(message.from_user.id, 'Ошибка. Повторите ввод', reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, set_max_size)
    else:
        hotels[message.from_user.id]['max_size'] = message.text
        bot.send_message(message.from_user.id, 'В каком городе искать отели?')
        bot.register_next_step_handler(message, city_location_markup)


def city_location_markup(message: 'Message') -> None:
    """Функция, запрашивает локацию для поиска"""

    city = message.text
    hotels[message.from_user.id]['city'] = city
    destination = rapidapi.rapidapi_search(city)
    if destination is None:
        bot.send_message(message.from_user.id, 'Ошибка подключения. Попробуй позже. Выполнить другой запрос?',
                         reply_markup=markup_retry)
        return
    if len(destination) == 0:
        bot.send_message(message.from_user.id, 'Запрашиваемый город не найден. Выполнить другой запрос??',
                         reply_markup=markup_retry)
        return
    hotels[message.from_user.id]['locations_list'] = destination
    location_markup = InlineKeyboardMarkup()
    for elem in destination.keys():
        location_markup.add(InlineKeyboardButton(text=elem, callback_data=elem))
    bot.send_message(message.from_user.id, 'В какой локации искать отели?', reply_markup=location_markup)


def choose_date_in(message: 'Message') -> None:
    """Функция, запрашивает дату заезда в отель"""

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

    try:
        location = hotels[message.from_user.id]['location']
        command = hotels[message.from_user.id]['command']
        destination_id = hotels[message.from_user.id]['locations_list'][location]
        max_size_page = int(hotels[message.from_user.id]['max_size'])
        date_in = hotels[message.from_user.id]['date_in']
        date_out = hotels[message.from_user.id]['date_out']
        bot.send_message(message.from_user.id, 'Ищу варианты...', reply_markup=ReplyKeyboardRemove())
        hotels[message.from_user.id]['hotels'] = rapidapi.hotel_info(destination_id, command, max_size_page, date_in, date_out)
        if hotels[message.from_user.id]['hotels'] is None:
            bot.send_message(message.from_user.id, 'Ошибка подключения. Попробуй позже. Выполнить другой запрос?',
                             reply_markup=markup_retry)
            hotels.clear()
            return
        if command == 'bestdeal':
            price = int(hotels[message.from_user.id]['max_price'])
            distance = float(hotels[message.from_user.id]['max_distance'])
            hotels[message.from_user.id]['hotels'] = rapidapi.select_best_hotels(
                hotels[message.from_user.id]['hotels'], price, distance, max_size_page
            )
        if len(hotels[message.from_user.id]['hotels']) == 0:
            bot.send_message(message.from_user.id,
                             'К сожалению по вашему запросу не найдено вариантов. Выполнить другой запрос??',
                             reply_markup=markup_retry)
            hotels.clear()
            return

        for elem in hotels[message.from_user.id]['hotels']:
            text = "\n\n".join((': '.join(('Отель', elem.name)),
                                ': '.join(('Адрес', elem.address)),
                                ': '.join(('Стоимость за все время', elem.price)),
                                ': '.join(('Удаленность от центра', elem.distance))))
            bot.send_message(message.from_user.id, text)

            if hotels[message.from_user.id]['show_photo'] == 'yes':
                max_photos = hotels[message.from_user.id]['max_photos']
                id_hotel = elem.id
                urls = rapidapi.hotel_photo(hotel_id=id_hotel, max_photos=int(max_photos))
                if urls is None:
                    bot.send_message(message.from_user.id, 'Ошибка подключения. Попробуй позже.Выполнить другой запрос?',
                                     reply_markup=markup_retry)
                    return
                for url in urls:
                    try:
                        bot.send_photo(message.from_user.id, url)
                    except ApiTelegramException:
                        bot.send_message(message.from_user.id, 'Произошла ошибка при загрузке фотографии',
                                         reply_markup=ReplyKeyboardRemove())

        flag = save_info_in_db(hotels)
        if not flag:
            bot.send_message(message.from_user.id, 'Не удалось записать данный запрос в историю')
        bot.send_message(message.from_user.id, 'Выполнить другой запрос?', reply_markup=markup_retry)
    except KeyError:
        bot.send_message(message.from_user.id, 'Извините, произошла ошибка. Выполнить другой запрос??',
                         reply_markup=markup_retry)
        hotels.clear()


if __name__ == '__main__':
    hotels = dict()
    bot.polling(none_stop=True, interval=0)
