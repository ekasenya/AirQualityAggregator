from main.models import Station, AirQService
import importlib
import logging


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
            logging.error('Refresh stations error:', ex)
