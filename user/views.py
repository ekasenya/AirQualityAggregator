import os

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.views.generic.edit import UpdateView
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
from django.db.models import Sum, When, Case
from django.db import models

from user.forms import SignUpForm, UserSettings
from user.models import UserProfile
from main.models import AirQService, Station, UserStations

from AirQualityAggregator.settings.base import STATIONS_PER_PAGE


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    template_name = "user/signup.html"

    def get_success_url(self):
        redirect_to = self.request.POST['next']
        return redirect_to

    def get_context_data(self, **kwargs):
        context = super(SignUpView, self).get_context_data(**kwargs)
        context.update({'next': self.request.GET.get('next', '')})
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        new_user = form.save()
        new_user.avatar = form.cleaned_data['avatar']
        new_user.save()

        login(self.request, new_user, 'django.contrib.auth.backends.ModelBackend')

        return response


class SettingsView(LoginRequiredMixin, UpdateView):
    form_class = UserSettings
    model = UserProfile
    template_name = 'user/user_settings.html'

    def get_success_url(self):
        redirect_to = self.request.POST['next']
        return redirect_to

    def get_context_data(self, **kwargs):
        context = super(SettingsView, self).get_context_data(**kwargs)
        context.update({'next': self.request.GET.get('next', '')})
        if self.request.user.avatar:
            context.update({'file_name': os.path.basename(self.request.user.avatar.name)})
        else:
            context.update({'file_name': ''})

        context.update({'pk': self.kwargs['pk']})
        context.update({'active_tab': 0})
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.user.email = form.data['email']
        if form.cleaned_data['avatar']:
            self.request.user.avatar = form.cleaned_data['avatar']
        self.request.user.save()

        return response


class StationSettingsView(LoginRequiredMixin, ListView):
    model = Station
    template_name = 'user/station_settings.html'
    context_object_name = 'station_list'
    paginate_by = STATIONS_PER_PAGE

    def get_success_url(self):
        redirect_to = self.request.POST['next']
        return redirect_to

    def get_context_data(self, **kwargs):
        context = super(StationSettingsView, self).get_context_data(**kwargs)
        context.update({'next': self.request.GET.get('next', '')})
        context.update({'pk': self.kwargs['pk']})
        context.update({'active_tab': 1})
        context.update({'my_stations': self.request.GET.get('my_stations', 0)})

        context.update({'service_id': int(self.request.GET.get('service_id', self.get_first_service()))})
        context.update({'service_list': AirQService.objects.all().order_by('name')})

        context.update({'q': self.request.GET.get('q', '')})

        return context

    def get_queryset(self):
        search_string = self.request.GET.get('q', None)
        qs = Station.objects.filter(service_id=self.request.GET.get('service_id', self.get_first_service()))

        if search_string:
            qs = qs.filter(name__icontains=search_string)

        user_id = self.request.user.id
        qs = qs.annotate(is_user_station=Sum(
            Case(When(userstations__user_id=user_id, then=1), default=0), output_field=models.IntegerField()))

        if self.request.GET.get('my_stations', 0) == '1':
            qs = qs.filter(is_user_station=1)

        return qs.order_by('name').values('id', 'name', 'is_user_station')

    def get_first_service(self):
        return AirQService.objects.all().order_by('name').first().id


@login_required
def select_station(request):
    station_id = request.POST.get('station_id')
    user_id = request.POST.get('user_id')

    user_station = UserStations.objects.filter(Q(station_id=station_id) & Q(user_id=user_id)).first()

    if user_station:
        user_station.delete()
        return HttpResponse(0)
    else:
        user_station = UserStations()
        user_station.user_id = user_id
        user_station.station_id = station_id
        user_station.save()
        return HttpResponse(1)

