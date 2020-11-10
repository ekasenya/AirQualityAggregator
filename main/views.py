from django.views.generic import TemplateView

from services.mos_eco_service import MosEcoService
from services.air_cms_service import AirCmsService
from services.custom_service import SUBSTANCE_DICT

from main.models import Measuring, MeasuringDetail, AirQService
from django.db.models import Avg


class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        service_data = {}
        for service in AirQService.objects.all():
            measure = Measuring.objects.filter(service_id=service.id).order_by('-createdate').first()

            if not measure:
                service_data[service.name] = []
                continue

            service_data[service.name] = list(
                MeasuringDetail.objects.filter(measuring_id=measure.id).select_related('substance') \
                    .values('substance_id', 'substance__shortname', 'substance__name_ru') \
                    .annotate(avg_value=Avg('value')).order_by('substance__shortname'))

        context.update({'service_data': service_data})

        return context
