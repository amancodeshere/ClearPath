import json
from decimal import Decimal

from src.repositories.db_repo import get_record, put_record
from src.repositories.s3_repo import read_file
from src.utils.weather_utils import decimal_converter


def temperature_classification(
    tempMin: int, tempMax: int, amTemp: int, pmTemp: int
):
    avgTemp = (tempMin + tempMax + amTemp + pmTemp) / 4

    if avgTemp < 15:
        return "Cold"
    elif avgTemp < 22:
        return "Mild"
    elif avgTemp < 30:
        return "Warm"
    else:
        return "Hot"


def rainfall_classification(rainfall: int):
    if rainfall == 0.0:
        return "No rain"
    elif rainfall < 10:
        return "Light rain"
    elif rainfall < 25:
        return "Moderate rain"
    else:
        return "Heavy rain"


def sunshine_classification(sunshineHours: int):
    sun_ratio = sunshineHours / 24
    if sun_ratio < 0.4:
        return "Cloudy"
    elif sun_ratio <= 0.8:
        return "Partly Cloudy"
    else:
        return "Sunny"


def wind_classification(windGustSpeed: int):
    if windGustSpeed < 20:
        return "Calm"
    elif windGustSpeed < 38:
        return "Breezy"
    elif windGustSpeed < 61:
        return "Windy"
    else:
        return "Gale"


def humidity_classification(amHumidity: int, pmHumidity: int):
    avgHumidity = (amHumidity + pmHumidity) / 2

    if avgHumidity <= 30:
        return "Low Humidity"
    elif avgHumidity <= 60:
        return "Moderate Humidity"
    elif avgHumidity <= 80:
        return "High Humidity"
    else:
        return "Extreme Humidity"


def process_collected_s3_object(key: str, eTag: str):
    content = read_file(key)

    date = content["events"][0]["event_attributes"]["date"]
    tempMin = content["events"][0]["event_attributes"]["tempMin"]
    tempMax = content["events"][0]["event_attributes"]["tempMax"]
    rainfall = content["events"][0]["event_attributes"]["rainfall"]
    sunshineHours = content["events"][0]["event_attributes"]["sunshineHours"]
    windGustSpeed = content["events"][0]["event_attributes"]["windGustSpeed"]
    amTemp = content["events"][0]["event_attributes"]["9am"]["temp"]
    amHumidity = content["events"][0]["event_attributes"]["9am"]["humidity"]
    pmTemp = content["events"][0]["event_attributes"]["3pm"]["temp"]
    pmHumidity = content["events"][0]["event_attributes"]["3pm"]["humidity"]

    temp_severity = temperature_classification(
        tempMin, tempMax, amTemp, pmTemp
    )
    rain_severity = rainfall_classification(rainfall)
    sunshine_severity = sunshine_classification(sunshineHours)
    wind_severity = wind_classification(windGustSpeed)
    humidity_severity = humidity_classification(amHumidity, pmHumidity)

    Item = {
        "Date": date,
        "eTag": eTag,
        "tempMin": Decimal(str(tempMin)),
        "tempMax": Decimal(str(tempMax)),
        "rainfall": Decimal(str(rainfall)),
        "sunshineHours": Decimal(str(sunshineHours)),
        "windGustSpeed": Decimal(str(windGustSpeed)),
        "9am": {
            "temp": Decimal(str(amTemp)),
            "humidity": Decimal(str(amHumidity)),
        },
        "3pm": {
            "temp": Decimal(str(pmTemp)),
            "humidity": Decimal(str(pmHumidity)),
        },
        "Weather_Severity": {
            "Temp_Severity": str(temp_severity),
            "Rain_Severity": str(rain_severity),
            "Sun_Severity": str(sunshine_severity),
            "Wind_Severity": str(wind_severity),
            "Humidity_Severity": str(humidity_severity),
        },
    }

    put_record(Item)


def return_weather_record(date: str):

    rec = get_record(date)
    return json.dumps(rec, default=decimal_converter, indent=4)
