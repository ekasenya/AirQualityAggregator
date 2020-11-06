import os

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.views.generic.edit import UpdateView
from django.views.generic import ListView

from user.forms import SignUpForm, UserSettings
from user.models import UserProfile
from main.models import AirQService, Station

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
        context.update({'my_stations': 1})

        context.update({'service_id': int(self.request.GET.get('service_id', self.get_first_service()))})
        context.update({'service_list': AirQService.objects.all().order_by('name')})

        context.update({'q': self.request.GET.get('q', '')})

        return context

    def get_queryset(self):
        search_string = self.request.GET.get('q', None)
        qs = Station.objects.filter(service_id=self.request.GET.get('service_id', self.get_first_service()))

        if search_string:
            qs = qs.filter(name__icontains=search_string)

        return qs.order_by('name')

    def get_first_service(self):
        return AirQService.objects.all().order_by('name').first().id

