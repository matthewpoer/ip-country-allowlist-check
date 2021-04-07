FROM python:3.9-slim

RUN mkdir -p /app/GeoLite2-Country_20210406
COPY handler.py /app
COPY GeoLite2-Country_20210406/GeoLite2-Country.mmdb /app/GeoLite2-Country_20210406/GeoLite2-Country.mmdb
COPY requirements.txt /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=handler.py
CMD flask run --host=0.0.0.0
