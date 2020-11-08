from django.db import models

from user.models import UserProfile


class AirQService(models.Model):
    name = models.CharField(max_length=64)
    url = models.CharField(max_length=128)
    stations_urn = models.CharField(max_length=128)
    average_urn = models.CharField(max_length=128)
    use_ssl = models.BooleanField(default=True)
    class_name = models.CharField(max_length=64, default='')


class Station(models.Model):
    service = models.ForeignKey(AirQService, on_delete=models.CASCADE)
    station_id = models.CharField(max_length=128)
    name = models.CharField(max_length=64)
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)
    address = models.CharField(max_length=256)
    create_date = models.DateTimeField(auto_now_add=True)


class UserStations(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)


class Substance(models.Model):
    shortname = models.CharField(max_length=8)
    name_ru = models.CharField(max_length=128)
    name_en = models.CharField(max_length=128)
    limit_value = models.FloatField()


class Measuring(models.Model):
    service = models.ForeignKey(AirQService, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    substance = models.ForeignKey(Substance, on_delete=models.CASCADE)
    value = models.FloatField(null=True)
    createdate = models.DateTimeField()
