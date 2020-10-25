from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('main/', include('main.urls')),
    path('user/', include('user.urls')),
    path('', RedirectView.as_view(url='main/')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
