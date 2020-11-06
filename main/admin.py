from django.contrib import admin

from main.models import AirQService, Station, UserStations

admin.site.register(AirQService)
admin.site.register(Station)
admin.site.register(UserStations)
