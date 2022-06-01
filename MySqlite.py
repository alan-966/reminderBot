import sqlite3
from datetime import date


class MySqlite:
	def __init__(self, db_name):
		self.db_name = db_name
		self.conn = sqlite3.connect(db_name)
		print('init', db_name)

	def createTable(self, table_name='birthdays'):
		try:
			cur = self.conn.cursor()
			cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_name}(
				id integer PRIMARY KEY autoincrement,
				first_name TEXT NOT NULL,
				last_name TEXT,
				patronymic TEXT,
				birthday TEXT);
			""")
			self.conn.commit()
			cur.close()
			return True
		except Exception as ex:
			print(ex)
			return False

	def dropTable(self, table_name='birthdays'):
		try:
			cur = self.conn.cursor()
			cur.execute(f"DROP TABLE {table_name}")
			cur.close()
			return True
		except Exception as ex:
			print(ex)
			return False

	def delete(self, current_id, table_name='birthdays'):
		try:
			cur = self.conn.cursor()
			cur.execute(f"DELETE FROM {table_name} WHERE id={current_id};")
			self.conn.commit()
			cur.close()
			return True
		except Exception as ex:
			print(ex)
			return False

	def getTables(self):
		try:
			cur = self.conn.cursor()
			cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
			print(cur.fetchall())
			cur.close()
			return True
		except Exception as ex:
			print(ex)
			return False

	def selectAll(self, table_name='birthdays'):
		try:
			cur = self.conn.cursor()
			cur.execute(f"SELECT * from {table_name}")
			print(*cur.fetchall(), sep='\n')
			cur.close()
			return True
		except Exception as ex:
			print(ex)
			return False

	def insert(self, rows, table_name='birthdays'):
		"""users=[(first_name, last_name, patronymic, birthday), (...)]"""
		if type(rows) != list:
			return False
		if len(rows) == 0:
			return False
		try:
			cur = self.conn.cursor()
			cur.executemany(f"""INSERT INTO {table_name}(
				first_name,
				last_name,
				patronymic,
				birthday
			) VALUES(?, ?, ?, ?);""", rows)
			self.conn.commit()
			cur.close()
			return True
		except Exception as ex:
			print(ex)
			return False

	def getBirthdayUsers(self, table_name='birthdays'):
		try:
			today = date.today().strftime('%d.%m.')
			cur = self.conn.cursor()
			cur.execute(f"SELECT * FROM {table_name} WHERE birthday LIKE '{today}%'")
			data = cur.fetchall()
			cur.close()
			sep = ''
			namesCount = len(data)
			if namesCount == 0:
				return False
			supportingWord = 'празднует' if namesCount == 1 else 'празднуют'
			if namesCount == 2:
				sep = ' и '
			else:
				sep = ', '
			names = sep.join([i[1] + ' ' + i[2] for i in data])

			return f'Сегодня {names} {supportingWord} День рождения!🎂🥳'
		except Exception as ex:
			print(ex)
			return False

	def __del__(self):
		self.conn.close()
		print('destructor')
