from django.views.generic import TemplateView

from services.MosEcoService import MosEcoService
from services.AirCmsService import AirCmsService
from services.CustomAirQualityService import SUBSTANCE_DICT


class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        mos_eco = MosEcoService()
        data = mos_eco.get_average_data()
        context.update({'mos_eco': data})

        air_cms = AirCmsService()
        data = air_cms.get_average_data()
        context.update({'air_cms': data})

        context.update({'substances': SUBSTANCE_DICT})

        return context
