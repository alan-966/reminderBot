import time
import telebot
from pygismeteo import Gismeteo
import schedule
from config import bot_token, clients_list, yandex_weather_key
from MySqlite import MySqlite
from datetime import datetime
import requests


def get_weather_yandex(**kwargs):
	try:
		part_name = {'night': 'Ночью', 'morning': 'Утром', 'day': 'Днём', 'evening': 'Вечером'}
		conditions = {
			'clear': 'ясно', 'partly-cloudy': 'малооблачно', 'cloudy': 'облачно с прояснениями',
			'overcast': 'пасмурно', 'drizzle': 'морось', 'light-rain': 'небольшой дождь',
			'rain': 'дождь', 'moderate-rain': 'умеренно сильный', 'heavy-rain': 'сильный дождь',
			'continuous-heavy-rain': 'длительный сильный дождь', 'showers': 'ливень',
			'wet-snow': 'дождь со снегом', 'light-snow': 'небольшой снег', 'snow': 'снег',
			'snow-showers': 'снегопад', 'hail': 'град', 'thunderstorm': 'гроза',
			'thunderstorm-with-rain': 'дождь с грозой', 'thunderstorm-with-hail': 'гроза с градом'
		}
		url_yandex = f'https://api.weather.yandex.ru/v2/informers/?lat={kwargs["lat"]}&lon={kwargs["lon"]}&lang=ru_RU'
		r = requests.get(url_yandex, headers={'X-Yandex-API-Key': yandex_weather_key}).json()
		current = r['fact']
		temp = f'{current["temp"]}°C'
		desc = conditions[current['condition']]
		hum = f'{current["humidity"]}%'
		pres = f'{current["pressure_mm"]}'

		message = 'Хорошего дня! \U0001F44D\U0001F609'
		message += f'\nСейчас — '
		message += f'Температура: {temp} ' if 'temp' in kwargs and kwargs['temp'] else ''
		message += f'{desc} ' if 'desc' in kwargs and kwargs['desc'] else ''
		message += f'Влажность: {hum} ' if 'hum' in kwargs and kwargs['hum'] else ''
		message += f'Давление: {pres} ' if 'pres' in kwargs and kwargs['pres'] else ''

		for i in r['forecast']['parts']:
			temp = f'{i["temp_min"]}°C...{i["temp_max"]}°C'
			desc = conditions[i['condition']]
			hum = f'{i["humidity"]}%'
			pres = f'{i["pressure_mm"]}'

			message += f'\n{part_name[i["part_name"]]} — '
			message += f'Температура: {temp} ' if 'temp' in kwargs and kwargs['temp'] else ''
			message += f'{desc} ' if 'desc' in kwargs and kwargs['desc'] else ''
			message += f'Влажность: {hum} ' if 'hum' in kwargs and kwargs['hum'] else ''
			message += f'Давление: {pres} ' if 'pres' in kwargs and kwargs['pres'] else ''
		return message
	except Exception as ex:
		return f'Ошибка при получении погоды: {ex}'


def get_weather_gismeteo(**kwargs):
	try:
		city = kwargs['city']
		gm = Gismeteo()
		city_id = gm.get_id_by_query(city)
		step3 = gm.step3(city_id, days=1)
		message = f'Прогноз погоды на сегодня в городе {city}:\n\U0000203C \U0001F447 \U0000203C'
		count = 0
		for i in step3:
			count += 1
			if count < 3:
				continue
			d = datetime.fromisoformat(i.date.local)
			t = d.strftime('%H:%M')
			temp = f'{i.temperature.air.c}°C'
			desc = i.description.full
			hum = f'{i.humidity.percent}%'
			pres = f'{i.pressure.mm_hg_atm}'
			icon = i.icon
			message += f'\n{t} — '
			message += f'Температура: {temp} ' if 'temp' in kwargs and kwargs['temp'] else ''
			message += f'{desc} ' if 'desc' in kwargs and kwargs['desc'] else ''
			message += f'Влажность: {hum} ' if 'hum' in kwargs and kwargs['hum'] else ''
			message += f'Давление: {pres} ' if 'pres' in kwargs and kwargs['pres'] else ''
		return message
	except Exception as ex:
		return f'Ошибка при получении погоды: {ex}'


def send_message(to=None, message=None):
	if to and message:
		bot = telebot.TeleBot(bot_token)
		bot.send_message(to, message)
		bot.stop_bot()


def catch_new_chat():
	bot = telebot.TeleBot(bot_token)

	@bot.message_handler(commands=['start'])
	def start_message(message):
		print(message.chat.id)

	bot.polling(none_stop=True)


def check_birthday_config(client, **kwargs):
	db = MySqlite(kwargs['db_name'])
	message = db.getBirthdayUsers(kwargs['table_name']) if 'table_name' in kwargs else db.getBirthdayUsers()
	if message:
		send_message(client, message)
	return schedule.CancelJob


def check_weather_config(client, **kwargs):
	message = ''
	if kwargs['service'] == 'gismeteo':
		message = get_weather_gismeteo(**kwargs)
	elif kwargs['service'] == 'yandex':
		message = get_weather_yandex(**kwargs)
	send_message(client, message)
	return schedule.CancelJob


def check_config():
	schedule.clear('action')
	for client in clients_list:
		for action in clients_list[client]:
			params = clients_list[client][action]
			t = params['time'] if 'time' in params else '00:00'
			if action == 'weather':
				schedule.every().day.at(t).do(check_weather_config, client, **params).tag('action')
			elif action == 'birthday':
				schedule.every().day.at(t).do(check_birthday_config, client, **params).tag('action')


def main():
	# catch_new_chat()
	check_config()
	schedule.every().day.at('00:00').do(check_config)
	while True:
		schedule.run_pending()
		time.sleep(1)


if __name__ == '__main__':
	main()
