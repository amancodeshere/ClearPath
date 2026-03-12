from src.dependencies.s3_client import s3_client, S3_BUCKET_NAME
from src.repositories.s3_repo import read_file
from src.repositories.db_repo import get_record
import urllib.parse

def temperature_classification(tempMin: int, tempMax: int, amTemp: int, pmTemp: int):
    avgTemp = (tempMin + tempMax + amTemp + pmTemp)/4
    print(avgTemp)
    if avgTemp < 15:
        return 'Cold'
    elif avgTemp < 22:
        return 'Mild'
    elif avgTemp < 30:
        return 'Warm'
    else:
        return 'Hot'

def rainfall_classification(rainfall: int):
    if rainfall == 0.0:
        return 'No rain'
    elif rainfall < 10:
        return 'Light rain'
    elif rainfall < 25:
        return 'Moderate rain'
    else:
        return 'Heavy rain'

def sunshine_classification(sunshineHours: int):
    print(sunshineHours)
    sun_ratio = sunshineHours / 24
    print(sun_ratio)

    if sun_ratio < 0.4:
        return 'Cloudy'
    elif sun_ratio <= 0.8:
        return 'Partly Cloudy'
    else:
        return 'Sunny'

def wind_classification(windGustSpeed: int):
    print(windGustSpeed)

    if windGustSpeed < 20:
        return 'Calm'
    elif windGustSpeed < 38:
        return 'Breezy'
    elif windGustSpeed < 61:
        return 'Windy'
    else:
        return 'Gale'

def humidity_classification(amHumidity: int, pmHumidity: int):
    print(amHumidity)

    avgHumidity = (amHumidity + pmHumidity) / 2
    print(avgHumidity)
    if avgHumidity <= 30:
        return 'Low Humidity'
    elif avgHumidity <= 60:
        return 'Moderate Humidity'
    elif avgHumidity <=80:
        return 'High Humidity'
    else:
        return 'Extreme Humidity'

def process_collected_s3_object(key: str, eTag: str):
    
    content = read_file(key)

    date = content['events'][0]['event_attributes']['date']
    tempMin = content['events'][0]['event_attributes']['tempMin']
    tempMax = content['events'][0]['event_attributes']['tempMax']
    rainfall = content['events'][0]['event_attributes']['rainfall']
    sunshineHours = content['events'][0]['event_attributes']['sunshineHours']
    windGustSpeed = content['events'][0]['event_attributes']['windGustSpeed']
    amTemp = content['events'][0]['event_attributes']['9am']['temp']
    amHumidity = content['events'][0]['event_attributes']['9am']['humidity']
    pmTemp = content['events'][0]['event_attributes']['3pm']['temp']
    pmHumidity = content['events'][0]['event_attributes']['3pm']['humidity']

    weather_severity = []
    weather_severity.append(temperature_classification(tempMin, tempMax, amTemp, pmTemp))
    weather_severity.append(rainfall_classification(rainfall))
    weather_severity.append(sunshine_classification(sunshineHours))
    weather_severity.append(wind_classification(windGustSpeed))
    weather_severity.append(humidity_classification(amHumidity, pmHumidity))
    
    print(date)