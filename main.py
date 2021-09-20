import telebot
import requests


if __name__ == '__main__':
    bot = telebot.TeleBot('2039006009:AAFnN7AU8onVVTe3tdwefEUIIkpzYJC7HpI')

    @bot.message_handler(content_types=['text'])
    def get_text_message(message: 'Message') -> None:
        """Функция для получения текстовых сообщений из telegram-бота.
        Объявляется слушатель для текстовых сообщений и обрабатываем их
        """

        if message.text.lower() == 'привет':
            bot.send_message(message.from_user.id, 'Привет. Я помогу найти лучший отель в твоем городе')
        elif message.text.lower() == '/hello_world':
            bot.send_message(message.from_user.id, 'Привет. Я помогу найти лучший отель в твоем городе')
        elif message.text == '/help':
            bot.send_message(message.from_user.id, 'Напиши "привет" или команду /hello_world')
        else:
            bot.send_message(message.from_user.id, 'Я не понимаю такую команду. Напиши /help')

    bot.polling(none_stop=True, interval=0)
