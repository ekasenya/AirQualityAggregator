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


class CustomAirQualityService:
    SERVICE_NAME = 'Air quality service'
    MAX_CONNECT_ATTEMPTS = 3
    NO_NAME = 'No name'

    def get_average_data(self):
        pass

    def get_stations(self):
        pass

    def get_station_data(self, station_id):
        pass

    def log_error(self, message):
        logging.error('{}. {}'.format(self.SERVICE_NAME, message))

    def log_info(self, message):
        logging.info('{}. {}'.format(self.SERVICE_NAME, message))
