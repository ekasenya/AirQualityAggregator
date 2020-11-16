import http.client
import logging
import ssl
from http import HTTPStatus

from main.models import AirQService


class AirQualityRequestError(Exception):
    pass


class CustomAirQualityService:
    SERVICE_NAME = 'Air quality service'
    MAX_CONNECT_ATTEMPTS = 3
    NO_NAME = 'No name'

    URL = ""
    
    NORMALIZE_RATE = 1

    def get_service_id(self):
        service = AirQService.objects.filter(url=self.URL).first()

        if not service:
            logging.error('Cannot get service if for {}'.format(self.__class__))
            return -1
        else:
            return service.id

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
                    conn.request("GET", self.DATA_URN)
                    response = conn.getresponse()

                    if response.status == HTTPStatus.OK:
                        return response.read()

                    self.log_error('Attempt #{} to get stations data failed.'.format(attempt + 1))
                finally:
                    conn.close()
            except Exception as ex:
                self.log_error('Attempt #{} to get stations data failed. Exception: {}'
                               .format(attempt + 1, ex))
        self.log_error('Can not get stations data')
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

    def get_all_stations_data(self):
        pass

    def log_error(self, message):
        logging.error('{}. {}'.format(self.SERVICE_NAME, message))

    def log_info(self, message):
        logging.info('{}. {}'.format(self.SERVICE_NAME, message))
