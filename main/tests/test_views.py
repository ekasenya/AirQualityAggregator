from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse

from main.models import AirQService, Station, Substance
from main.tests.fixtures import AirQServiceFactory, StationFactory, MeasuringFactory, MeasuringDetailFactory, \
    SubstanceFactory


class IndexViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        service = AirQServiceFactory()

        stations = StationFactory.create_batch(5, service=service)
        measuring = MeasuringFactory(service=service, createdate=datetime.now())
        substances = SubstanceFactory.create_batch(4)

        for substance in substances:
            for station in stations:
                MeasuringDetailFactory(measuring=measuring, substance=substance, station=station)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/main/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/index.html')

    def test_lists_all_measurings(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['service_data']) == 1)


class SubstanceDetailView(TestCase):
    @classmethod
    def setUpTestData(cls):
        service = AirQServiceFactory()

        stations = StationFactory.create_batch(5, service=service)
        measuring = MeasuringFactory(service=service, createdate=datetime.now())
        substances = SubstanceFactory.create_batch(4)

        for substance in substances:
            for station in stations:
                MeasuringDetailFactory(measuring=measuring, substance=substance, station=station)

    def get_url(self):
        service_id = AirQService.objects.all().first().id
        substance_id = Substance.objects.all().first().id
        station_id = Station.objects.all().first().id

        return '/main/service/{}/{}/{}'.format(service_id, station_id, substance_id)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/substance_detail.html')

    def test_search_detail_info(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

        service_id = AirQService.objects.all().first().id
        self.assertTrue(response.context['last_value'] > 0)
        self.assertTrue(int(response.context['service_id']) == service_id)

