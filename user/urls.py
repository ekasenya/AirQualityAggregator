from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^login/$', auth_views.LoginView.as_view(template_name='user/login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(template_name='user/logout.html'), name='logout'),
    url(r'^signup$', views.SignUpView.as_view(), name='signup'),
    url(r'^settings/(?P<pk>[0-9]+)/$', views.SettingsView.as_view(), name='settings'),
    url(r'^station-settings/(?P<pk>[0-9]+)/$', views.StationSettingsView.as_view(), name='station-settings'),
    url(r'^ajax/station-settings/select/$', views.select_station, name='select_station'),
]
