from src.dependencies.s3_client import s3_client, S3_BUCKET_NAME
from src.repositories.s3_repo import read_file
from src.repositories.db_repo import put_record
import urllib.parse
from decimal import Decimal

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

    print(type(tempMax))

    temp_severity = temperature_classification(tempMin, tempMax, amTemp, pmTemp)
    rain_severity = rainfall_classification(rainfall)
    sunshine_severity = sunshine_classification(sunshineHours)
    wind_severity = wind_classification(windGustSpeed)
    humidity_severity = humidity_classification(amHumidity, pmHumidity)
    
    Item = {
        'Date': date,
        'tempMin': Decimal(str(tempMin)),
        'tempMax': Decimal(str(tempMax)),
        'rainfall': Decimal(str(rainfall)),
        'sunshineHours': Decimal(str(sunshineHours)),
        'windGustSpeed': Decimal(str(windGustSpeed)),
        '9am': {
            'temp': Decimal(str(amTemp)),
            'humidity': Decimal(str(amHumidity))
        },
        '3pm': {
            'temp': Decimal(str(pmTemp)),
            'humidity': Decimal(str(pmHumidity))
        },
        'Weather_Severity': {
            'Temp_Severity': str(temp_severity), 
            'Rain_Severity': str(rain_severity),
            'Sun_Severity': str(sunshine_severity),
            'Wind_Severity': str(wind_severity),
            'Humidity_Severity': str(humidity_severity)
            }
    }

    put_record(Item)
    print(date)