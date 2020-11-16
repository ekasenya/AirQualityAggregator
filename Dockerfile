
FROM python:3
ENV PYTHONUNBUFFERED 1
COPY . /code/AirQualityAggregator/
#RUN git clone https://github.com/katty87/AirQualityAggregator.git /code/AirQualityAggregator/
WORKDIR /code/AirQualityAggregator
#SECRET_KEY = "$(openssl rand -base64 50)"
COPY requirements.txt /code/
RUN pip install -r requirements.txt