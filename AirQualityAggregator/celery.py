from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from django.conf import settings

from main.tasks import pull_data

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AirQualityAggregator.settings.dev')

app = Celery('AirQualityAggregator')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls pull_data every 15 minutes.
    sender.add_periodic_task(15.0 * 60, pull_data.s(), name='pull data')




