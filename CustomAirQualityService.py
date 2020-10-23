import logging

class CustomAirQualityService:
    SERVICE_NAME = 'Air quality service'
    MAX_CONNECT_ATTEMPTS = 3

    def get_stations(self):
        pass

    def get_station_data(self):
        pass

    def log_error(self, message):
        logging.error('{}. {}'.format(self.SERVICE_NAME, message))

    def log_info(self, message):
        logging.info('{}. {}'.format(self.SERVICE_NAME, message))
