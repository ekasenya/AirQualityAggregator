import importlib
import logging
from datetime import datetime

from main.models import Measuring, Substance, MeasuringDetail
from main.models import Station, AirQService


def refresh_station_list():
    for service in AirQService.objects.all():
        try:
            module_path, _, class_name = service.class_name.rpartition('.')
            module = importlib.import_module(module_path)
            class_ = getattr(module, class_name)
            instance = class_()

            station_list = instance.get_stations()

            if not station_list:
                continue

            for key, value in station_list.items():
                if not Station.objects.filter(station_id=key):
                    station = Station()
                    station.service = service
                    station.station_id = key
                    station.name_ru = value
                    station.save()

        except Exception as ex:
            logging.error('Refresh station list error:', ex)


def pull_stations_data():

    for service in AirQService.objects.all():
        try:
            module_path, _, class_name = service.class_name.rpartition('.')
            module = importlib.import_module(module_path)
            class_ = getattr(module, class_name)
            instance = class_()

            logging.info("Start pulling data. Service: {}".format(class_name))
            service = instance.get_service()

            if not service:
                logging.info("Service id not found: {}".format(class_name))
                continue

            service_id = service.id

            measuring = Measuring()
            measuring.service_id = service_id
            measuring.createdate = datetime.now()
            measuring.save()

            stations_data = instance.get_all_stations_data()
            if stations_data:
                for station_id, substance_dict in stations_data.items():
                    for key, value in substance_dict.items():
                        substance = Substance.objects.filter(shortname=key).first()
                        if not substance:
                            logging.error('Substance {} not found'.format(key))
                            continue

                        measuring_det = MeasuringDetail()
                        measuring_det.measuring = measuring
                        measuring_det.station_id = station_id
                        measuring_det.substance = substance
                        try:
                            measuring_det.value = float(value) / instance.NORMALIZE_RATE
                        except ValueError:
                            measuring_det.value = None
                        measuring_det.save()

        except Exception as ex:
            logging.error('Refresh stations data error:', ex)

        logging.info("Finish pulling data. Service: {}".format(class_name))
