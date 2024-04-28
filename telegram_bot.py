import requests

from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta

TOKEN = ""

API_KEY = ""

CITY_NAME_TO_CITY = {
    "Dublin": "Dublin,Ireland",
    "Vienna": "Vienna,Austria",
    "Moscow": "Moscow,Russia"
}

bot = TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(row_width=3)
    for city_name in CITY_NAME_TO_CITY.keys():
        item_button = KeyboardButton(city_name)
        markup.add(item_button)
    bot.send_message(message.chat.id, "Choose the city:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in CITY_NAME_TO_CITY.keys())
def send_temperature(message):
    city_name = message.text
    city = CITY_NAME_TO_CITY[city_name]
    current_datetime = hour_rounder(date_time=datetime.now())
    current_date = current_datetime.date()
    weather_by_hours = get_weather_by_date_and_city(date=str(current_date), city=city)
    current_time = current_datetime.time()
    for hourly_weather in weather_by_hours:
        if hourly_weather.get("datetime") == str(current_time):
            fahrenheit_temperature = hourly_weather.get("temp")
            temperature = fahrenheit_to_celsius(fahrenheit_temperature=fahrenheit_temperature)
            bot.send_message(message.chat.id, f"The temperature in {city_name} now is {temperature} degrees Celsius.")


def get_weather_by_date_and_city(*, date: str, city: str) -> list[dict]:
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/{date}/{date}?unitGroup=us&key={API_KEY}"
    response = requests.get(url)
    weather_by_days = response.json()["days"]
    weather_by_hours = weather_by_days[0]["hours"]
    return weather_by_hours


def fahrenheit_to_celsius(*, fahrenheit_temperature: float) -> int:
    return round((fahrenheit_temperature - 32) * 5 / 9)


def hour_rounder(*, date_time: datetime) -> datetime:
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return date_time.replace(second=0, microsecond=0, minute=0, hour=date_time.hour) + timedelta(
        hours=date_time.minute // 30)


bot.infinity_polling()
