from django.views.generic import TemplateView, ListView

from datetime import datetime

from main.models import Measuring, MeasuringDetail, AirQService, Substance, UserStations
from django.db.models import Avg, Q
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

        service_data = {}
        for service in AirQService.objects.all():
            measure = Measuring.objects.filter(service_id=service.id).order_by('-createdate').first()

            if not measure:
                service_data[service.id] = []
                continue

            if my_stations == '1':
                stations = UserStations.objects.select_related('station')\
                    .filter(station__service_id=service.id, user_id=self.request.user.id)\
                    .values('station_id')

                station_data = {}
                for station in stations:
                    values = MeasuringDetail.objects.filter(measuring_id=measure.id, station_id=station['station_id'])\
                            .select_related('substance')\
                            .values('substance_id', 'substance__shortname', 'substance__name_ru')\
                            .annotate(avg_value=Avg('value')).order_by('substance__shortname')

                    #if len(values):
                    station_data[station['station_id']] = list(values)

                service_data[service.id] = station_data
            else:
                service_data[service.id] = list(
                    MeasuringDetail.objects.filter(measuring_id=measure.id).select_related('substance') \
                        .values('substance_id', 'substance__shortname', 'substance__name_ru') \
                        .annotate(avg_value=Avg('value')).order_by('substance__shortname'))

        context.update({'service_data': service_data})
        context.update({'my_stations': my_stations})

        return context


class SubstanceDetailView(TemplateView):
    template_name = 'main/substance_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SubstanceDetailView, self).get_context_data(**kwargs)

        service_id = kwargs['service_id']
        substance_id = kwargs['substance_id']

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
        plt.axhline(substance.limit_value, color='red', ls='--')
        plt.plot(hours, values, color='blue', marker='o')
        plt.ylim(0, 1.5 * substance.limit_value)
        plt.grid(True)

        fig = plt.gcf()
        buf = io.BytesIO()

        fig.savefig(buf, format="png")
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        context.update({'graph': uri})

        return context
