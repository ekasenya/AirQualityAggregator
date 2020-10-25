from django.views.generic import TemplateView

from services.MosEcoService import MosEcoService
from services.CustomAirQualityService import SUBSTANCE_DICT


class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        mos_eco = MosEcoService()
        data = mos_eco.get_average_data()

        context.update({'list': data})
        context.update({'substances': SUBSTANCE_DICT})

        return context
