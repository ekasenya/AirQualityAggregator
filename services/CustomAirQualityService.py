import http.client
from http import HTTPStatus
import ssl

import logging


SUBSTANCE_DICT = \
    {
        "NO2": "Диоксид азота",
        "NO": "Оксид азота",
        "CO": "Оксид углерода",
        "O3": "Озон приземный",
        "PM10": "Взвешенные частицы PM10",
        "PM2,5": "Взвешенные частицы PM2.5",
        "SO2": "Серы диоксид",
        "H2S": "Сероводород",
        "CH4": "Метан",
        "C8H8": "Стирол",
        "C6H6": "Бензол",
        "C10H8": "Нафталин",
        "CH2O": "Формальдегид",
        "C6H5OH": "Фенол",
        "C7H8": "Толуол",
    }

PDK_DICT = \
    {
        "NO2": "0.2",
        "NO": "0",
        "CO": "0",
        "O3": "0.16",
        "PM10": "0.3",
        "PM2,5": "0",
        "SO2": "0",
        "H2S": "0",
        "CH4": "0",
        "C8H8": "0",
        "C6H6": "0",
        "C10H8": "0",
        "CH2O": "0",
        "C6H5OH": "0",
        "C7H8": "0",
    }


class AirQualityRequestError(Exception):
    pass


class CustomAirQualityService:
    SERVICE_NAME = 'Air quality service'
    MAX_CONNECT_ATTEMPTS = 3
    NO_NAME = 'No name'

    URL = ""
    STATIONS_URN = ""
    AVERAGE_URN = ""

    def get_average_data(self):
        response_data = self.request_average_data()

        if not response_data:
            return

        return self.parse_average_data(response_data)

    def request_average_data(self):
        if not self.URL:
            raise AirQualityRequestError('Url is empty')

        if not self.URL:
            raise AirQualityRequestError('Average data urn is empty')

        context = ssl._create_unverified_context()

        for attempt in range(self.MAX_CONNECT_ATTEMPTS):
            try:
                conn = http.client.HTTPSConnection(self.URL, context=context)
                try:
                    conn.request("GET", self.AVERAGE_URN)
                    response = conn.getresponse()

                    if response.status == HTTPStatus.OK:
                        return response.read()

                    self.log_error('Attempt #{} to get average data failed.'.format(attempt + 1))
                finally:
                    conn.close()
            except Exception as ex:
                self.log_error('Attempt #{} to get average data failed. Exception: {}'
                               .format(attempt + 1, ex))
        self.log_error('Can not get average list')
        return

    def parse_average_data(self, response_data):
        pass

    def get_stations(self):
        response_data = self.request_station_list()

        if not response_data:
            return

        station_list = self.parse_station_list(response_data)

        return station_list

    def request_station_list(self):
        if not self.STATIONS_URN:
            raise AirQualityRequestError('Url is empty')

        context = ssl._create_unverified_context()

        for attempt in range(self.MAX_CONNECT_ATTEMPTS):
            try:
                conn = http.client.HTTPSConnection(self.URL, context=context)
                try:
                    conn.request("GET", self.STATIONS_URN)
                    response = conn.getresponse()

                    if response.status == HTTPStatus.OK:
                        return response.read()

                    self.log_error('Attempt #{} to get station list failed.'.format(attempt + 1))
                finally:
                    conn.close()
            except Exception as ex:
                self.log_error('Attempt #{} to get station list failed. Exception: {}'
                               .format(attempt + 1, ex))
        self.log_error('Can not get station list')
        return

    def parse_station_list(self, response_data):
        pass

    def get_station_data(self, station_id):
        pass

    def log_error(self, message):
        logging.error('{}. {}'.format(self.SERVICE_NAME, message))

    def log_info(self, message):
        logging.info('{}. {}'.format(self.SERVICE_NAME, message))
