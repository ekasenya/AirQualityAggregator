FROM python:3
ENV PYTHONUNBUFFERED 1
RUN git clone https://github.com/katty87/AirQualityAggregator.git /code/AirQualityAggregator/
WORKDIR /code/AirQualityAggregator
RUN SECRET_KEY="$(openssl rand -base64 50)"
COPY requirements.txt /code/
RUN pip install -r requirements.txt