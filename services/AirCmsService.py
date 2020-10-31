import json
import http.client
from http import HTTPStatus
import ssl

from services.CustomAirQualityService import CustomAirQualityService


class AirCmsService(CustomAirQualityService):
    SERVICE_NAME = 'Air civic monitoring system'
    MAX_CONNECT_ATTEMPTS = 3

    SCHEME = "https://"
    URL = "aircms.online"
    STATIONS_URN = "/php/guiapi.php?devices"
    AVERAGE_URN = "/php/guiapi.php?T=0"

    MIN_LAT = 55.5
    MAX_LAT = 56
    MIN_LON = 37
    MAX_LON = 38

    NORMALIZE_RATE = 1000

    SUBSTANCE_MATCHING_DICT = {
        "sds_p1": "PM10",
        "sds_p2": "PM2,5",
    }

    devices = {}

    def parse_average_data(self, response_data):
        summary_data = {
            "sds_p1": 0,
            "sds_p2": 0
        }

        cnt = 0

        self.get_stations()
        data = json.loads(response_data)['data']

        for item in data:
            if item['device_id'] in self.devices:
                summary_data['sds_p1'] += float(item['sds_p1'])
                summary_data['sds_p2'] += float(item['sds_p2'])
                cnt += 1

        result = {}
        if cnt:
            for key in summary_data.keys():
                result[self.SUBSTANCE_MATCHING_DICT[key]] = round(summary_data[key]/(cnt * self.NORMALIZE_RATE), 3)

        return result

    def get_stations(self):
        if self.devices:
            return self.devices

        return super().get_stations()

    def parse_station_list(self, response_data):
        data = json.loads(response_data)['data']

        self.devices.clear()
        for item in data:
            lat = float(item['lat'])
            lon = float(item['lon'])

            if (self.MIN_LAT <= lat <= self.MAX_LAT) and (self.MIN_LON <= lon <= self.MAX_LON):
                self.devices[item['id']] = item['address']

    def get_station_data(self, station_id):
        pass
