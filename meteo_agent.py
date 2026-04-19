#!/usr/bin/env python3
import os
import sys
from datetime import datetime

import requests
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherFetchError(Exception):
    pass


class WhatsAppSendError(Exception):
    pass


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

    try:
        response = requests.get(OPENWEATHER_URL, params=params, timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        response = exc.response
        status_code = response.status_code if response is not None else "N/A"
        response_text = response.text if response is not None else "N/A"
        raise WeatherFetchError(
            f"Errore meteo per '{query_city}': status={status_code}, body={response_text}"
        ) from exc
    except requests.RequestException as exc:
        raise WeatherFetchError(f"Errore rete durante richiesta meteo per '{query_city}': {exc}") from exc


def format_message(weather: dict, city_label: str) -> str:
    main = weather.get("main", {})
    weather_info = (weather.get("weather") or [{}])[0]
    wind = weather.get("wind", {})

    temp = main.get("temp")
    feels_like = main.get("feels_like")
    humidity = main.get("humidity")
    condition = weather_info.get("description", "condizioni non disponibili")
    wind_speed = wind.get("speed")
    temp_display = f"{temp}°C" if temp is not None else "N/D"
    feels_like_display = f"{feels_like}°C" if feels_like is not None else "N/D"
    humidity_display = f"{humidity}%" if humidity is not None else "N/D"
    wind_speed_display = f"{wind_speed} m/s" if wind_speed is not None else "N/D"

    today = datetime.now().strftime("%d/%m/%Y")

    return (
        f"🌞 Buongiorno! Ecco il meteo di oggi ({today}) per {city_label}:\n\n"
        f"🌡️ Temperatura: {temp_display}\n"
        f"🤗 Percepita: {feels_like_display}\n"
        f"☁️ Condizioni: {condition}\n"
        f"💧 Umidità: {humidity_display}\n"
        f"💨 Vento: {wind_speed_display}\n\n"
        "Buona giornata! 🚀"
    )


def send_whatsapp_message(account_sid: str, auth_token: str, from_number: str, to_number: str, body: str) -> str:
    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            from_=from_number,
            to=to_number,
            body=body,
        )
        return message.sid
    except TwilioRestException as exc:
        raise WhatsAppSendError(
            f"Invio WhatsApp fallito (from={from_number}, to={to_number}): "
            f"code={exc.code}, status={exc.status}, msg={exc.msg}"
        ) from exc


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
    except (WeatherFetchError, WhatsAppSendError) as exc:
        print(str(exc), file=sys.stderr)
    except Exception as exc:
        print(f"Errore: {exc}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
