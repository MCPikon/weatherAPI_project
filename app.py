"""WeatherAPI App - Python 3.11.5"""

from datetime import datetime
import requests
import os
from dotenv import load_dotenv
from typing import Final
import pyfiglet
from simple_chalk import chalk
from http import HTTPStatus

# Loads .env file with the environment variables
load_dotenv()

# Constants
API_KEY: Final[str] = os.getenv("API_KEY")
BASE_URL: Final[str] = "http://api.openweathermap.org/data/2.5/weather"

WEATHER_ICONS: Final[dict] = {
    # day icons
    "01d": "☀️",
    "02d": "⛅️",
    "03d": "☁️",
    "04d": "☁️",
    "09d": "🌧",
    "10d": "🌦",
    "11d": "⛈",
    "13d": "🌨",
    "50d": "🌫",
    # night icons
    "01n": "🌙",
    "02n": "☁️",
    "03n": "☁️",
    "04n": "☁️",
    "09n": "🌧",
    "10n": "🌦",
    "11n": "⛈",
    "13n": "🌨",
    "50n": "🌫",
}


def main() -> None:
    """Main function"""
    city: str = input(
        chalk.bold("Introduce la ciudad de la que quieras consultar el tiempo : ")
    )
    metric_unit: str = input(
        chalk.bold(
            "¿Quieres ver los datos en medidas métricas (Cº y km/h) o imperiales (Fº y mph)? (m/i. Default: m) : "
        )
    )
    output: str = get_weather_from_city(city, metric_unit)
    print(output)


def get_cardinal_from_degrees(wind_degrees: int) -> str:
    """Return the cardinal direction that corresponds to the degree that is passed by parameter"""
    DIRECTIONS: list = ["N ↑", "NE ↗", "E →", "SE ↘", "S ↓", "SO ↙", "O ←", "NO ↖"]
    degrees = wind_degrees * 8 / 360
    degrees = round(degrees)
    degrees = (degrees + 8) % 8
    return DIRECTIONS[degrees]


def get_weather_from_city(city: str, metric_unit) -> str:
    """Returns the weather of the city that is passed by parameter"""
    if metric_unit.lower() == "i":
        units = "imperial"
        degrees_symbol = "ºF"
        wind_speed_unit = "mph"
    else:
        units = "metric"
        degrees_symbol = "ºC"
        wind_speed_unit = "km/h"

    url: str = f"{BASE_URL}?appid={API_KEY}&q={city}&units={units}"

    response = requests.get(url)

    if response.status_code == HTTPStatus.OK.value:
        # get parameters
        weather_json: dict = response.json()
        country: str = weather_json["sys"]["country"]
        temp: float = weather_json["main"]["temp"]
        feels_like_temp: float = weather_json["main"]["feels_like"]
        temp_max: float = weather_json["main"]["temp_max"]
        temp_min: float = weather_json["main"]["temp_min"]
        wind_speed: float = weather_json["wind"]["speed"]
        wind_degrees: int = weather_json["wind"]["deg"]
        humidity: int = weather_json["main"]["humidity"]
        icon_code = weather_json["weather"][0]["icon"]
        weather_icon: str = WEATHER_ICONS.get(icon_code)
        sunrise_time: str = datetime.utcfromtimestamp(
            weather_json["sys"]["sunrise"] + weather_json["timezone"]
        ).strftime("%H:%M")
        sunset_time: str = datetime.utcfromtimestamp(
            weather_json["sys"]["sunset"] + weather_json["timezone"]
        ).strftime("%H:%M")

        # other parameters
        pressure: int = weather_json["main"]["pressure"]
        cloudiness: int = weather_json["clouds"]["all"]

        output: str = f"{pyfiglet.figlet_format(city)}\n"
        output += chalk.bold(
            f"{weather_icon}  La temperatura en {city} ({country}) es de {round(temp)}{degrees_symbol}"
            f" | (Mínima: {round(temp_min)}{degrees_symbol} / Máxima: {round(temp_max)}{degrees_symbol})\n"
        )
        output += chalk.magentaBright(
            f"❄ La sensación térmica es de {round(feels_like_temp)}{degrees_symbol}\n"
        )
        output += chalk.cyan(f"💧 La humedad es del {humidity}%\n")
        output += chalk.green(
            f"🍃 La velocidad del viento es de {wind_speed*3.6:.2f} {wind_speed_unit}"
            f" (🧭 Dirección del viento: {get_cardinal_from_degrees(wind_degrees)})\n"
        )
        output += chalk.yellow(f"☀ Amanece a las {sunrise_time} (hora local)\n")
        output += chalk.blue(f"🌒 Anochece a las {sunset_time} (hora local)\n\n")
        output += chalk.bold(f"Otros datos:\n")
        output += f"-> 🌍 La presión atmosférica es de {pressure} hPa\n"
        output += f"-> ☁ La nubosidad es del {cloudiness}%"

    elif response.status_code == HTTPStatus.NOT_FOUND.value:
        output: str = chalk.yellow(
            f"🕵️‍♀️ No se ha encontrado la ciudad: {city} (Prueba a ejecutar la app y volver a escribirla)"
        )

    elif response.status_code == HTTPStatus.UNAUTHORIZED.value:
        output: str = chalk.red(f"🛑 ERROR: El API_KEY no es válido.")

    else:
        output: str = chalk.red(
            f"❌ Se ha producido un error al obtener la información del tiempo para {chalk.bold(city)}"
        )

    return output


if __name__ == "__main__":
    main()
