from typing import Optional, List, Dict, Any
import requests
from loguru import logger


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

    def __init__(self, city: str, api_key: Optional[Any] = None) -> None:
        self.max_size = 15
        self.api_key = api_key
        self.url_search: str = 'https://hotels4.p.rapidapi.com/locations/search'
        self.url_properties_list: str = 'https://hotels4.p.rapidapi.com/properties/list'
        self.url_hotel_photos: str = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'

    @logger.catch
    def rapidapi_search(self, city) -> Optional[Dict[str, str]]:
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
        except Exception:
            logger.error('Error in request rapidapi-search')
            return None

        destination_id: Dict[str, str] = dict()
        response_dict = response.json()
        for value in response_dict['suggestions'][0]['entities']:
            destination_id[value['name']] = value['destinationId']

        return destination_id

    @logger.catch
    def hotel_info(self, destination_id, option: str, max_size: int, date_in: str, date_out: str) -> Optional[List['Hotel']]:
        """Метод класса, делает get-запрос на сайт
        https://rapidapi.com/apidojo/api/hotels4/,
        получают информацию об отелях.

        :return: list с объектами Hotel.
        """

        sort_order: str = ''
        if option == 'low' or option is None:
            sort_order = 'PRICE'
        elif sort_order == 'high':
            sort_order = 'PRICE_HIGHEST_FIRST'
        else:
            sort_order = 'DISTANCE_FROM_LANDMARK'

        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': f"{self.api_key}"
        }

        if destination_id is None:
            return None

        if max_size > self.max_size:
            max_size = self.max_size

        hotels: list = list()
        querystring = {
            "destinationId": f"{destination_id}", "pageNumber": "1", "pageSize": f"{max_size}",
            "checkIn": f"{date_in}", "checkOut": f"{date_out}", "adults1": "1", "sortOrder": f"{sort_order}",
            "locale": "ru_RU", "currency": "RUB"
        }

        try:
            logger.info('request rapidapi-properties_list')
            response = requests.get(self.url_properties_list, params=querystring, headers=headers)
        except Exception:
            logger.error('Error in request rapidapi-properties_list')
            if len(hotels) > 0:
                return None
            else:
                return hotels

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
