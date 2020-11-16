import http.client
import ssl
from http import HTTPStatus

from bs4 import BeautifulSoup

from main.models import Station
from services.custom_service import CustomAirQualityService


class MosEcoService(CustomAirQualityService):
    URL = "mosecom.mos.ru"

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

        return self.parse_station_data(html)

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

    def parse_station_data(self, response_data):
        result = {}

        parser = BeautifulSoup(markup=response_data.decode("utf-8"), features='html.parser')
        for item in parser.find_all("div", class_="m-flip__content"):
            type = item.find("div", class_="text-norma")
            if not type:
                continue

            count = item.find("span", class_="this-count")

            result[type.contents[0].strip()] = count.contents[0].strip() if count else None
        return result

    def get_all_stations_data(self):
        service_id = self.get_service_id()

        if service_id <= 0:
            return

        station_list = Station.objects.filter(service_id=service_id)

        station_data = {}
        for station in station_list:
            response_data = self.request_station_data(station.station_id)
            if not response_data:
                continue

            substance_dict = self.parse_station_data(response_data)
            if substance_dict:
                station_data[station.id] = substance_dict

        return station_data

    def parse_all_stations_data(self, response_data):
        result = {}

        parser = BeautifulSoup(markup=response_data.decode("utf-8"), features='html.parser')
        for item in parser.find_all("div", class_="m-flip__content"):
            type = item.find("div", class_="text-norma")
            if not type:
                continue

            count = item.find("span", class_="this-count")

            result[type.contents[0].strip()] = count.contents[0].strip() if count else None
        return result
