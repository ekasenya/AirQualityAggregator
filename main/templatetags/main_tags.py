from django import template

from services.custom_service import  SUBSTANCE_DICT

register = template.Library()


@register.filter(name='get_dict_value')
def get_dict_value(dict, key):
    if key in dict:
        return dict[key]
    else:
        return 'Unknown'
