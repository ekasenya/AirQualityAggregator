from datetime import datetime

from django.test import TestCase

from main.models import UserStations
from user.models import UserProfile
from user.tests.fixtures import UserFactory
from main.tests.fixtures import UserStationsFactory, StationFactory, AirQServiceFactory


class UserStationsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = UserFactory()
        station = StationFactory(service=AirQServiceFactory())
        UserStationsFactory(user=user, station=station)

    def test_user_stations(self):
        user1 = UserProfile.objects.all()[0]
        user_stations = UserStations.objects.filter(user=user1)
        self.assertEqual(len(user_stations), 1)

