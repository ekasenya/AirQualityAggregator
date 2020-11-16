#!/usr/bin/env bash
cd /code/AirQualityAggregator
pwd
python3 manage.py flush --no-input
python3 manage.py migrate --no-input
python3 manage.py test --no-input
if [[ $? -eq 0 ]]
then
    python3 manage.py runserver 0.0.0.0:80
fi;
