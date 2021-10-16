from typing import Optional, List, Dict, Any
import requests
from loguru import logger
from requests.exceptions import ReadTimeout, ConnectTimeout, ConnectionError, Timeout, HTTPError


class Hotel:
    """ Класс, хранит информацию об отеле."""

    def __init__(self) -> None:
        self.id = None
        self.name = None
        self.price = None
        self.address = None
        self.distance = None


class RapidApi:
    """ Класс, работает с API сайта https://rapidapi.com/apidojo/api/hotels4/"""

    def __init__(self, api_key: Optional[Any] = None) -> None:
        self.max_size = 15
        self.max_photos = 30
        self.api_key = api_key
        self.url_search: str = 'https://hotels4.p.rapidapi.com/locations/search'
        self.url_properties_list: str = 'https://hotels4.p.rapidapi.com/properties/list'
        self.url_hotel_photos: str = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'

    @logger.catch
    def rapidapi_search(self, city: str) -> Optional[Dict[str, str]]:
        """
        Метод класса, делает get-запрос на сайт
        https://rapidapi.com/apidojo/api/hotels4/

        :return: dict наименовании локации: destination id; None, если запрос прошел неудачно.
        """

        querystring = {"query":f"{city}","locale":"ru_RU"}
        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': f"{self.api_key}"
        }

        try:
            logger.info('request rapidapi-search')
            response = requests.get(self.url_search, params=querystring, headers=headers, timeout=10)
        except (ReadTimeout, ConnectTimeout, Timeout):
            print('The request timed out or The server did not send any data in the allotted amount of time'
                  'or The request timed out while trying to connect to the remote server.')
            logger.error('Error in request rapidapi-search')
            return None
        except (ConnectionError, HTTPError):
            print('A Connection error occurred or An HTTP error occurred.')
            logger.error('Error in request rapidapi-search')
            return None

        destination_id: Dict[str, str] = dict()
        response_dict = response.json()
        for value in response_dict['suggestions'][0]['entities']:
            destination_id[value['name']] = value['destinationId']

        return destination_id

    @logger.catch
    def select_best_hotels(self, hotels: List['Hotel'], max_price: float, max_distance: float, max_size: int) -> List['Hotel']:
        """Метод класса, отсортировывает отели из переданного списка
        по условиям: не более максимальной стоимости max_price и
        не дальше максимальной удаленности от центра города max_distance.

        :return: list с объектами Hotel.
        """

        res_list: List['Hotel'] = list()
        for hotel in hotels:
            if len(res_list) >= max_size:
                break
            price = hotel.price.split()[0]
            price = price.split(',')
            price = int(''.join(price))
            distance = hotel.distance.split()[0]
            distance = distance.split(',')
            distance = float('.'.join(distance))
            if price <= max_price and distance <= max_distance:
                res_list.append(hotel)

        return res_list

    @logger.catch
    def hotel_info(self, destination_id: str, option: str, max_size: int, date_in: str, date_out: str) -> Optional[List['Hotel']]:
        """Метод класса, делает get-запрос на сайт
        https://rapidapi.com/apidojo/api/hotels4/,
        получают информацию об отелях.

        :return: list с объектами Hotel; None, если запрос прошел неудачно.
        """

        sort_order = ''
        logger.info(''.join(('Выполняется команда ', option)))
        if option == "lowprice":
            sort_order = 'PRICE'
        elif option == "highprice":
            sort_order = 'PRICE_HIGHEST_FIRST'
        elif option == "bestdeal":
            sort_order = 'DISTANCE_FROM_LANDMARK'

        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': f"{self.api_key}"
        }

        if destination_id is None:
            return None

        if sort_order == 'DISTANCE_FROM_LANDMARK':
            max_size = 25
        elif max_size > self.max_size:
            max_size = self.max_size

        hotels: list = list()
        if sort_order == 'DISTANCE_FROM_LANDMARK':
            querystring = {
                "destinationId": f"{destination_id}", "pageNumber": "1", "pageSize": f"{max_size}",
                "checkIn": f"{date_in}", "checkOut": f"{date_out}", "adults1": "1", "sortOrder": f"{sort_order}",
                "locale": "ru_RU", "currency": "RUB", "landmarkIds": "Центр города"
            }
        else:
            querystring = {
                "destinationId": f"{destination_id}", "pageNumber": "1", "pageSize": f"{max_size}",
                "checkIn": f"{date_in}", "checkOut": f"{date_out}", "adults1": "1", "sortOrder": f"{sort_order}",
                "locale": "ru_RU", "currency": "RUB"
            }

        try:
            logger.info('request rapidapi-properties_list')
            response = requests.get(self.url_properties_list, params=querystring, headers=headers, timeout=10)
        except (ReadTimeout, ConnectTimeout, Timeout):
            print('The request timed out or The server did not send any data in the allotted amount of time '
                  'or The request timed out while trying to connect to the remote server.')
            logger.error('Error in request rapidapi-properties_list')
            return None
        except (ConnectionError, HTTPError):
            print('A Connection error occurred or An HTTP error occurred.')
            logger.error('Error in request rapidapi-properties_list')
            return None

        hotel_dict = response.json()
        for elem in hotel_dict['data']['body']['searchResults']['results']:
            hotel = Hotel()
            try:
                hotel.name = elem['name']
                hotel.address = ', '.join((elem['address']['locality'], elem['address']['streetAddress']))
                hotel.price = elem['ratePlan']['price']['current']
                hotel.distance = elem['landmarks'][0]['distance']
                hotel.id = elem['id']
                hotels.append(hotel)
            except KeyError:
                continue

        return hotels

    @logger.catch
    def hotel_photo(self, hotel_id: str, max_photos: int) -> Optional[List[str]]:
        """Метод класса, делает get-запрос на сайт
        https://rapidapi.com/apidojo/api/hotels4/,
        получает фотографии выбранного отеля по id.

        :return: list с объектами Hotel; None, если запрос прошел неудачно.
        """

        if max_photos > self.max_photos:
            max_photos = self.max_photos

        querystring = {"id": f"{hotel_id}"}
        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': f"{self.api_key}"
        }

        try:
            logger.info('request rapidapi-find_photo')
            response_dict = requests.get(self.url_hotel_photos, params=querystring, headers=headers, timeout=10).json()
        except (ReadTimeout, ConnectTimeout, Timeout):
            print('The request timed out or The server did not send any data in the allotted amount of time')
            logger.error('Error in request rapidapi-find_photo')
            return None
        except (ConnectionError, HTTPError):
            print('A Connection error occurred or An HTTP error occurred.')
            logger.error('Error in request rapidapi-find_photo')
            return None

        size = 'w'
        photo_urls: List[str] = list()
        i = 1
        for value in response_dict['hotelImages']:
            if i > max_photos:
                break
            photo_urls.append(value['baseUrl'].format(size=size))
            i += 1

        return photo_urls
