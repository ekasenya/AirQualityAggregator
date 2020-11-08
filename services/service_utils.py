from main.models import Station, AirQService
import importlib
import logging

from datetime import datetime
from main.models import Measuring, Substance


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
                    station.name = value
                    station.save()

        except Exception as ex:
            logging.error('Refresh station list error:', ex)


def pull_stations_data():

    createdate = datetime.now()

    for service in AirQService.objects.all():
        try:
            module_path, _, class_name = service.class_name.rpartition('.')
            module = importlib.import_module(module_path)
            class_ = getattr(module, class_name)
            instance = class_()

            service_id = instance.get_service_id()

            if service_id <= 0:
                continue

            stations_data = instance.get_all_stations_data()
            if stations_data:
                for station_id, substance_dict in stations_data.items():
                    for key, value in substance_dict.items():
                        substance = Substance.objects.filter(shortname=key).first()
                        if not substance:
                            logging.error('Substance {} not found'.format(key))
                            continue

                        measuring = Measuring()
                        measuring.service_id = service_id
                        measuring.station_id = station_id
                        measuring.substance = substance
                        try:
                            measuring.value = float(value)
                        except ValueError:
                            measuring.value = None
                        measuring.createdate = createdate
                        measuring.save()
        except Exception as ex:
            logging.error('Refresh stations data error:', ex)
