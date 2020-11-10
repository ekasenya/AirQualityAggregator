from celery import Celery

app = Celery('AirQualityAggregator')


@app.task
def pull_data():
    print('!'*40, 'pull data', '!'*40)
    from services.service_utils import pull_stations_data
    pull_stations_data()
