from loader import bot
from loader import markup
from loader import help_text
from handler import save_info_in_file


@bot.message_handler(content_types=['text'])
def get_text_message(message: 'Message') -> None:
    """Функция для получения текстовых сообщений из telegram-бота.
    Объявляется слушатель для текстовых сообщений и их обработчик
    """

    if message.text.lower() == 'привет' or message.text.lower() == '/start':
        bot.send_message(message.from_user.id, 'Привет. Я помогу найти лучший отель в твоем городе', reply_markup=markup)
    elif message.text == 'Найти дешевые' or message.text == '/lowprice':
        bot.send_message(message.from_user.id, 'Ищу самые дешёвые отели в городе')
        save_info_in_file(message.from_user.id, '/lowprice')
    elif message.text == 'Найти дорогие' or message.text == '/highprice':
        bot.send_message(message.from_user.id, 'Ищу самые дорогие отели в городе')
        save_info_in_file(message.from_user.id, '/highprice')
    elif message.text == 'Лучшие предложения' or message.text == '/bestdeal':
        bot.send_message(message.from_user.id, 'Ищу наиболее подходящие отели по цене и расположению от центра')
        save_info_in_file(message.from_user.id, '/bestdeal')
    elif message.text == 'Помощь' or message.text == '/help':
        bot.send_message(message.from_user.id, help_text, reply_markup=markup)
    elif message.text == 'История поиска' or message.text == '/history':
        bot.send_message(message.from_user.id, 'История поиска отелей:')
    else:
        bot.send_message(message.from_user.id, 'Я не понимаю такую команду. Напиши /help', reply_markup=markup)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
