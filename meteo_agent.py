#!/usr/bin/env python3
import os
import sys
from datetime import datetime

import requests
from twilio.rest import Client

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_env(name: str, required: bool = True, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if required and not value:
        raise ValueError(f"Variabile ambiente mancante: {name}")
    return value


def get_weather(city: str, api_key: str, country_code: str | None = None, units: str = "metric", lang: str = "it") -> dict:
    query_city = city if not country_code else f"{city},{country_code}"
    params = {
        "q": query_city,
        "appid": api_key,
        "units": units,
        "lang": lang,
    }

    response = requests.get(OPENWEATHER_URL, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def format_message(weather: dict, city_label: str) -> str:
    main = weather.get("main", {})
    weather_info = (weather.get("weather") or [{}])[0]
    wind = weather.get("wind", {})

    temp = main.get("temp")
    feels_like = main.get("feels_like")
    humidity = main.get("humidity")
    condition = weather_info.get("description", "condizioni non disponibili")
    wind_speed = wind.get("speed")

    today = datetime.now().strftime("%d/%m/%Y")

    return (
        f"🌞 Buongiorno! Ecco il meteo di oggi ({today}) per {city_label}:\n\n"
        f"🌡️ Temperatura: {temp}°C\n"
        f"🤗 Percepita: {feels_like}°C\n"
        f"☁️ Condizioni: {condition}\n"
        f"💧 Umidità: {humidity}%\n"
        f"💨 Vento: {wind_speed} m/s\n\n"
        "Buona giornata! 🚀"
    )


def send_whatsapp_message(account_sid: str, auth_token: str, from_number: str, to_number: str, body: str) -> str:
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_=from_number,
        to=to_number,
        body=body,
    )
    return message.sid


def main() -> int:
    try:
        city = get_env("CITY_NAME")
        country_code = get_env("COUNTRY_CODE", required=False)
        weather_api_key = get_env("OPENWEATHER_API_KEY")

        account_sid = get_env("TWILIO_ACCOUNT_SID")
        auth_token = get_env("TWILIO_AUTH_TOKEN")
        from_whatsapp = get_env("TWILIO_WHATSAPP_FROM")
        to_whatsapp = get_env("TWILIO_WHATSAPP_TO")

        weather = get_weather(city=city, api_key=weather_api_key, country_code=country_code)
        city_label = weather.get("name") or city
        message = format_message(weather, city_label)

        sid = send_whatsapp_message(
            account_sid=account_sid,
            auth_token=auth_token,
            from_number=from_whatsapp,
            to_number=to_whatsapp,
            body=message,
        )

        print(f"Messaggio WhatsApp inviato con successo. SID: {sid}")
        return 0
    except requests.HTTPError as exc:
        print(f"Errore HTTP durante chiamata meteo: {exc}", file=sys.stderr)
    except Exception as exc:
        print(f"Errore: {exc}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
