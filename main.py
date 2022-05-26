import telebot
import schedule
import time
import config
from MySqlite import MySqlite


def telegram_bot():
    bot = telebot.TeleBot(config.token)

    @bot.message_handler(commands=['start'])
    def start_message(message):
        print(message.chat.id)
        bot.send_message(config.test_chat_id, 'Привет Alan')

    bot.polling(none_stop=True)


def sqlite():
    testDB = MySqlite('test.db')
    # users = [
    #     ('Gamesh', 'Tahohov', 'Vissarionovich', '27.05.2005'),
    # ]
    # testDB.insert(users)
    testDB.selectAll()
    print()
    data = testDB.selectBirthdayUsers()

    sep = ''
    if len(data) == 2:
        sep = ' и '
    else:
        sep = ', '
    names = [i[1] + ' ' + i[2] for i in data]
    print(names)
    print(sep.join(names))
    # print(*data, sep='\n')


def main():
    sqlite()
    # schedule.every(5).seconds.do(sqlite)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    # telegram_bot()


if __name__ == '__main__':
    main()
