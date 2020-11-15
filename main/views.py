from django.views.generic import TemplateView, ListView

from datetime import datetime

from main.models import Measuring, MeasuringDetail, AirQService, Substance, UserStations
from django.db.models import Avg, Q, Value, IntegerField
from django.db.models.functions import TruncHour

import urllib, base64
import io
import matplotlib.pyplot as plt

import matplotlib

matplotlib.use('Agg')


class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        my_stations = self.request.GET.get('my_stations', '0')
        group_type = self.request.GET.get('group_type', '0')

        if group_type == '0':
            service_data = self.get_service_data_by_services(my_stations)
        else:
            service_data = self.get_service_data_by_substance(my_stations)

        context.update({'service_data': service_data})
        context.update({'my_stations': my_stations})
        context.update({'group_type': self.request.GET.get('group_type', '0')})

        return context

    def get_service_data_by_services(self, my_stations):
        service_data = {}
        for service in AirQService.objects.all():
            measure = Measuring.objects.filter(service_id=service.id).order_by('-createdate').first()

            if not measure:
                service_data[service.id] = []
                continue

            if my_stations == '1':
                stations = UserStations.objects.select_related('station') \
                    .filter(station__service_id=service.id, user_id=self.request.user.id) \
                    .values('station_id')

                station_data = {}
                for station in stations:
                    values = MeasuringDetail.objects.filter(measuring_id=measure.id, station_id=station['station_id']) \
                        .select_related('substance').filter(substance__show=True) \
                        .values('substance_id', 'substance__shortname', 'substance__name_ru') \
                        .annotate(avg_value=Avg('value')).order_by('substance__shortname')

                    if len(values):
                        station_data[station['station_id']] = list(values)

                service_data[service.id] = station_data
            else:
                service_data[service.id] = list(
                    MeasuringDetail.objects.filter(measuring_id=measure.id).select_related('substance') \
                        .filter(substance__show=True)
                        .values('substance_id', 'substance__shortname', 'substance__name_ru') \
                        .annotate(avg_value=Avg('value')).order_by('substance__shortname'))

        return service_data

    def get_service_data_by_substance(self, my_stations):
        service_data = {}
        for substance in Substance.objects.filter(show=True):
            if my_stations == '1':
                substances = Substance.objects.filter(show=True)

                service_data = {}
                for substance in substances:
                    service_data[substance.id] = []

                    for service in AirQService.objects.all():
                        measure = Measuring.objects.filter(service_id=service.id).order_by('-createdate').first()
                        stations = UserStations.objects.select_related('station') \
                            .filter(station__service_id=service.id, user_id=self.request.user.id) \
                            .values('station_id')

                        values = MeasuringDetail.objects.filter(measuring_id=measure.id, substance_id=substance.id,
                                                                station_id__in=stations) \
                            .select_related('station').filter(substance__show=True) \
                            .values('station__station_id', 'station__name') \
                            .annotate(avg_value=Avg('value'))

                        if len(values):
                            not_none_values = list(filter(lambda item: item['avg_value'], list(values)))
                            service_data[substance.id].extend(not_none_values)

            else:
                service_data[substance.id] = []
                for service in AirQService.objects.all():
                    measure = Measuring.objects.filter(service_id=service.id).order_by('-createdate').first()

                    qs = MeasuringDetail.objects.filter(measuring_id=measure.id, substance_id=substance.id) \
                        .select_related('substance') \
                        .annotate(service_id=Value(service.id, output_field=IntegerField())) \
                        .values('service_id', 'substance__shortname', 'substance__name_ru') \
                        .annotate(avg_value=Avg('value')).order_by('substance__shortname')

                    if len(qs):
                        service_data[substance.id].append(qs.first())

        return service_data


class CustomSubstanceDetailView(TemplateView):
    pass


class SubstanceDetailView(CustomSubstanceDetailView):
    template_name = 'main/substance_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SubstanceDetailView, self).get_context_data(**kwargs)

        service_id = kwargs['service_id']
        substance_id = kwargs['substance_id']

        context.update({'service_id': service_id})

        measure = Measuring.objects.filter(service_id=service_id).order_by('-createdate').first()
        substance = Substance.objects.get(id=substance_id)
        context.update({'last_datetime': measure.createdate.strftime('%d.%m.%Y %H:%M')})
        context.update({'last_value': MeasuringDetail.objects.
                       filter(Q(measuring_id=measure.id) & Q(substance_id=substance_id)).first().value})
        context.update({'substance_name': substance.name_ru})

        today = datetime.today()
        measuring_qs = Measuring.objects.filter(createdate__year=today.year, createdate__month=today.month,
                                                createdate__day=12, service_id=service_id)

        # value_qs = MeasuringDetail.objects.filter(substance_id=substance_id, measuring__in=measuring_qs). \
        #    select_related('measuring').values('measuring__createdate') \
        #    .annotate(avg_value=Avg('value')).order_by('measuring__createdate')

        value_qs = MeasuringDetail.objects.filter(substance_id=substance_id, measuring__in=measuring_qs) \
            .select_related('measuring').values('measuring__createdate') \
            .annotate(hour=TruncHour('measuring__createdate')).values('hour') \
            .annotate(avg_value=Avg('value')).values('hour', 'avg_value').order_by('hour')

        values = []
        hours = []
        for item in value_qs:
            values.append(round(item['avg_value'], 3))
            hours.append('{}:00'.format(str(item['hour'].hour).zfill(2)))

        plt.style.use('seaborn-whitegrid')
        plt.cla()
        plt.axhline(substance.limit_value, color='red', ls='--', label="ПДК")
        plt.plot(hours, values, color='blue', marker='o')
        plt.ylim(0, 1.5 * substance.limit_value)
        plt.legend(numpoints=1)
        plt.grid(True)

        fig = plt.gcf()
        buf = io.BytesIO()

        fig.savefig(buf, format="png")
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        context.update({'graph': uri})

        return context


class SubstanceServicesDetailView(CustomSubstanceDetailView):
    template_name = 'main/substance_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SubstanceServicesDetailView, self).get_context_data(**kwargs)

        context.update({'service_id': '0'})

        substance_id = kwargs['substance_id']
        substance = Substance.objects.get(id=substance_id)
        context.update({'substance_name': substance.name_ru})

        plt.style.use('seaborn-whitegrid')
        plt.cla()
        plt.axhline(substance.limit_value, color='red', ls='--', label="ПДК")

        last_measuring_data = []
        today = datetime.today()
        for station in UserStations.objects.select_related('station') \
                .filter(user_id=self.request.user.id) \
                .values('station_id', 'station__service_id', 'station__name'):
            measure = Measuring.objects.filter(service_id=station['station__service_id']).order_by(
                '-createdate').first()

            last_value_qs = MeasuringDetail.objects.filter(measuring_id=measure.id, substance_id=substance_id) \
                .first()

            if not last_value_qs:
                continue

            last_measuring_data.append(
                {'name': station['station__name'],
                 'last_datetime': measure.createdate.strftime('%d.%m.%Y %H:%M'),
                 'last_value': MeasuringDetail.objects.filter(Q(measuring_id=measure.id) & Q(substance_id=substance_id)) \
                     .first().value})

            measuring_qs = Measuring.objects.filter(createdate__year=today.year, createdate__month=today.month,
                                                    createdate__day=12)

            value_qs = MeasuringDetail.objects.filter(substance_id=substance_id, measuring__in=measuring_qs,
                                                      station_id=station.id) \
                .select_related('measuring').values('measuring__createdate') \
                .annotate(hour=TruncHour('measuring__createdate')).values('hour') \
                .annotate(avg_value=Avg('value')).values('hour', 'avg_value').order_by('hour')

            values = []
            hours = []
            for item in value_qs:
                values.append(round(item['avg_value'], 3))
                hours.append('{}:00'.format(str(item['hour'].hour).zfill(2)))

            plt.plot(hours, values, marker='o', label=station.name)

        context.update({'last_measuring_data': last_measuring_data})

        plt.ylim(0, 1.5 * substance.limit_value)
        plt.legend(numpoints=1)
        plt.grid(True)

        fig = plt.gcf()
        buf = io.BytesIO()

        fig.savefig(buf, format="png")
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        context.update({'graph': uri})

        return context


class SubstanceStationsDetailView(CustomSubstanceDetailView):
    template_name = 'main/substance_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SubstanceStationsDetailView, self).get_context_data(**kwargs)

        context.update({'service_id': '0'})

        substance_id = kwargs['substance_id']
        substance = Substance.objects.get(id=substance_id)
        context.update({'substance_name': substance.name_ru})

        plt.style.use('seaborn-whitegrid')
        plt.cla()
        plt.axhline(substance.limit_value, color='red', ls='--', label="ПДК")

        last_measuring_data = []
        today = datetime.today()
        for service in AirQService.objects.all():
            measure = Measuring.objects.filter(service_id=service.id).order_by('-createdate').first()

            last_value_qs = MeasuringDetail.objects.filter(measuring_id=measure.id, substance_id=substance_id) \
                .first()

            if not last_value_qs:
                continue

            last_measuring_data.append(
                {'name': service.name, 'last_datetime': measure.createdate.strftime('%d.%m.%Y %H:%M'),
                 'last_value': MeasuringDetail.objects.filter(Q(measuring_id=measure.id) & Q(substance_id=substance_id)) \
                     .first().value})

            measuring_qs = Measuring.objects.filter(createdate__year=today.year, createdate__month=today.month,
                                                    createdate__day=12, service_id=service.id)

            value_qs = MeasuringDetail.objects.filter(substance_id=substance_id, measuring__in=measuring_qs) \
                .select_related('measuring').values('measuring__createdate') \
                .annotate(hour=TruncHour('measuring__createdate')).values('hour') \
                .annotate(avg_value=Avg('value')).values('hour', 'avg_value').order_by('hour')

            values = []
            hours = []
            for item in value_qs:
                values.append(round(item['avg_value'], 3))
                hours.append('{}:00'.format(str(item['hour'].hour).zfill(2)))

            plt.plot(hours, values, marker='o', label=service.name)

        context.update({'last_measuring_data': last_measuring_data})

        plt.ylim(0, 1.5 * substance.limit_value)
        plt.legend(numpoints=1)
        plt.grid(True)

        fig = plt.gcf()
        buf = io.BytesIO()

        fig.savefig(buf, format="png")
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        context.update({'graph': uri})

        return context
