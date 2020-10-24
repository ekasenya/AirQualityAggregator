import http.client
from http import HTTPStatus
from bs4 import BeautifulSoup

import CustomAirQualityService


class MosEcoService(CustomAirQualityService):
    URL = "https://mosecom.mos.ru"
    STATIONS_URN = "/stations/"
    SERVICE_NAME = "MosEcoMonitoring"

    def request_station_list(self):
        attempt = 0
        try:
            with http.client.HTTPSConnection(self.URL) as conn:
                conn.request("GET", self.STATIONS_URN)
                response = conn.getresponse()

                if response.status != HTTPStatus.OK:
                    self.log_error('Attempt #{} to get station list failed.'.format(attempt + 1))
                    if attempt >= self.MAX_CONNECT_ATTEMPTS:
                        self.log_error('Can not get station list')
                        return

                return response.read()
        except Exception as ex:
            self.log_error('Request station list failed. {}'.format(ex))

    def parse_station_list_html(self, html):
        parser = BeautifulSoup(markup=html.decode("utf-8"), features='html.parser')

    def get_stations(self):
        station_list = {}
        html = self.request_station_list()

        if not html:
            return station_list

        station_list = self.parse_station_list_html(html)

    def get_station_data(self):
        pass
