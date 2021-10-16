from datetime import datetime
from loguru import logger
import sqlite3 as sq
from typing import Optional


@logger.catch
def save_info_in_db(data_dict: dict) -> bool:
    """Функция, сохраняет историю запросов пользователя в базу данных."""

    logger.info('Сохранение в базу данных')
    user_id = 0
    for key in data_dict.keys():
        user_id = key
        break
    command = data_dict[user_id]['command']
    fmt = "%d.%m.%Y - %H:%M:%S"
    date_time = datetime.now().strftime(fmt)
    city = data_dict[user_id]['city']
    location = data_dict[user_id]['location']
    hotels = ''
    for elem in data_dict[user_id]['hotels']:
        hotels = '\n\n'.join((hotels, "\n".join((': '.join(('Отель', elem.name)), ': '.join(('Адрес', elem.address))))))

    with sq.connect('history.db') as connect_db:
        cur = connect_db.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS history_requests (
        user_id INTEGER,
        date_time TEXT,
        city TEXT,
        location TEXT,
        command TEXT,
        hotels TEXT
        )""")

        try:
            cur.execute("INSERT INTO history_requests (user_id, date_time, city, location, command, hotels) "
                        "VALUES ({}, '{}', '{}', '{}', '{}', '{}')".format(user_id, date_time, city, location, command, hotels))
        except sq.OperationalError:
            logger.error('Ошибка записи в БД')
            return False

    return True


@logger.catch
def load_info_db(user_id: int) -> Optional[list]:
    """Функция, загружает историю запросов пользователя из базы данных по id."""

    logger.info('Загрузка из базы данных')
    try:
        with sq.connect('history.db') as connect_db:
            cur = connect_db.cursor()
            cur.execute("SELECT * FROM (SELECT * FROM history_requests WHERE user_id == {}"
                        " ORDER BY date_time DESC LIMIT 10) t ORDER BY date_time".format(user_id))
            res = cur.fetchall()
            return res
    except sq.OperationalError:
        logger.error('Таблица не найдена: history_requests')
        print('Таблица не найдена')
        return None
