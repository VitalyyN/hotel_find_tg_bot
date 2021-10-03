from datetime import datetime
from loguru import logger


@logger.catch
def save_info_in_file(user_id: int, command: str, city: str = '') -> None:
    """Функция, сохраняет историю запросов пользователя в файл.
    Имя файла содержит id Телеграмм пользователя, имеет расширение .info.
    """

    logger.info(' - '.join(('-'.join(('user_id', str(user_id))), command)))
    command = ''.join(('Запрос: ', command))
    fmt = '%Y.%m.%d %H:%M:%S'
    text = ' - '.join((datetime.now().strftime(fmt), command))
    city = ' - '.join(('Город:', city))
    text = '; '.join((text, city))
    file_name: str = ''.join((str(user_id), '.info'))
    with open(file_name, 'a', encoding='utf-8') as file:
        file.write(text)
        file.write('\n')
