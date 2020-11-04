import http.client
from http import HTTPStatus
from bs4 import BeautifulSoup
import ssl

from services.CustomAirQualityService import CustomAirQualityService


class MosEcoService(CustomAirQualityService):
    SCHEME = "https://"
    URL = "mosecom.mos.ru"
    STATIONS_URN = "/stations/"
    AVERAGE_URN = "/vozdux/"
    SERVICE_NAME = "MosEcoMonitoring"

    def parse_average_data(self, response_data):
        result = {}

        parser = BeautifulSoup(markup=response_data.decode("utf-8"), features='html.parser')
        for item in parser.find_all("div", class_="item-block m-flip lm4 count-green"):
            type = item.find("div", class_="text-norma")
            if not type:
                continue

            count = item.find("span", class_="this-count")
            result[type.contents[0].strip()] = count.contents[0].strip() if count else None
        return result

    def get_stations(self):
        response_data = self.request_station_list()

        if not response_data:
            return

        station_list = self.parse_station_list(response_data)

        return station_list

    def request_station_list(self):
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
        result = {}

        parser = BeautifulSoup(markup=response_data.decode("utf-8"), features='html.parser')
        for item in parser.find_all("div", class_="row-title"):
            info = item.find("a")
            if info:
                ref = info.attrs['href']
                if len(info) > 1:
                    name = info.contents[2].strip()
                else:
                    name = self.NO_NAME

                if ref:
                    prefix = self.SCHEME + self.URL
                    if ref.startswith(prefix):
                        ref = ref[len(prefix):]
                    result[ref] = name
        return result

    def get_station_data(self, station_id):
        html = self.request_station_data(station_id)

        if not html:
            return

        return self.parse_station_data_html(html)

    def request_station_data(self, station_id):
        context = ssl._create_unverified_context()

        for attempt in range(self.MAX_CONNECT_ATTEMPTS):
            try:
                conn = http.client.HTTPSConnection(self.URL, context=context)
                try:
                    conn.request("GET", station_id)
                    response = conn.getresponse()

                    if response.status == HTTPStatus.OK:
                        return response.read()

                    self.log_error('Attempt #{} to get station {} data failed.'
                                   .format(station_id, attempt + 1))
                finally:
                    conn.close()
            except Exception as ex:
                self.log_error('Attempt #{} to get station {} data failed. Exception: {}'
                               .format(station_id, attempt + 1, ex))
        self.log_error('Can not get station {} data'.format(station_id))
        return

    def parse_station_data_html(self, html):
        result = {}

        parser = BeautifulSoup(markup=html.decode("utf-8"), features='html.parser')
        for item in parser.find_all("div", class_="m-flip__content"):
            type = item.find("div", class_="text-norma")
            if not type:
                continue

            count = item.find("span", class_="this-count")

            result[type.contents[0].strip()] = count.contents[0].strip() if count else None
        return result
