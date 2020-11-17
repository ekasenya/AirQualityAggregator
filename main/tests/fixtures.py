from datetime import datetime

import factory

from main.models import AirQService, Station, UserStations, Substance, Measuring, MeasuringDetail
from user.tests.fixtures import UserFactory


class AirQServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AirQService

    name_ru = factory.Sequence(lambda n: "service%s" % n)


class StationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Station

    name_ru = factory.Sequence(lambda n: "station%s" % n)
    service = factory.SubFactory(AirQServiceFactory)


class UserStationsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserStations

    user = factory.SubFactory(UserFactory)
    station = factory.SubFactory(Station)


class SubstanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Substance

    name_ru = factory.Sequence(lambda n: "substance%s" % n)
    limit_value = 0.03


class MeasuringFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Measuring

    service = factory.SubFactory(AirQServiceFactory)
    createdate = factory.LazyFunction(datetime.now)


class MeasuringDetailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MeasuringDetail

    measuring = factory.SubFactory(MeasuringFactory)
    value = 0.01


