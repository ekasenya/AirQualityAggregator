from django import template

from main.models import AirQService, Station, Substance

register = template.Library()


@register.filter(name='get_dict_value')
def get_dict_value(dict, key):
    if key in dict:
        return dict[key]
    else:
        return 'Unknown'


@register.filter(name='get_service_name')
def get_service_name(id):
    try:
        service = AirQService.objects.get(id=id)
        return service.name_ru
    except Exception as ex:
        return 'Unknown'


@register.filter(name='get_station_name')
def get_station_name(id):
    try:
        station = Station.objects.get(id=id)
        return station.name_ru
    except Exception as ex:
        return 'Unknown'


@register.filter(name='get_substance_name')
def get_substance_name(id):
    try:
        substance = Substance.objects.get(id=id)
        return substance.name_ru
    except Exception as ex:
        return 'Unknown'
