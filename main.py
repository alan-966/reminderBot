import time
import telebot
from pygismeteo import Gismeteo
import schedule
from config import bot_token, clients_list
from MySqlite import MySqlite
from datetime import datetime


def get_weather(city):
	try:
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
			message += f'\n{t} — Температура: {temp} {desc}, Влажность: {hum}, Давление: {pres}'
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


def sqlite():
	db = MySqlite('moyidei.db')
	data = db.getBirthdayUsers()
	print(data)


def main():
	for client in clients_list:
		for action in clients_list[client]:
			if action == 'weather':
				params = clients_list[client][action]
				message = get_weather(params['city'])
				send_message(client, message)
			elif action == 'birthday':
				pass

	# print(get_weather('Владикавказ'))
	# send_message()
	# catch_new_chat()
	# sqlite()
	# schedule.every(5).seconds.do(asd)
	# while True:
	# 	schedule.run_pending()
	# 	time.sleep(1)


if __name__ == '__main__':
	main()
