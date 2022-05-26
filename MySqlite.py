import sqlite3
from datetime import date


class MySqlite:
	def __init__(self, db_name):
		self.db_name = db_name
		self.conn = sqlite3.connect(db_name)
		print('init', db_name)

	def createTable(self, table_name='users'):
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

	def dropTable(self, table_name='users'):
		cur = self.conn.cursor()
		cur.execute(f"DROP TABLE {table_name}")
		cur.close()

	def delete(self, current_id, table_name='users'):
		cur = self.conn.cursor()
		cur.execute(f"DELETE FROM {table_name} WHERE id={current_id};")
		self.conn.commit()
		cur.close()

	def getTables(self):
		cur = self.conn.cursor()
		cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
		print(cur.fetchall())
		cur.close()

	def selectAll(self, table_name='users'):
		cur = self.conn.cursor()
		cur.execute(f"SELECT * from {table_name}")
		print(*cur.fetchall(), sep='\n')
		cur.close()

	def insert(self, users=[], table_name='users'):
		"""users=[(first_name, last_name, patronymic, birthday), (...)]"""
		if len(users) == 0:
			return False

		cur = self.conn.cursor()
		cur.executemany(f"""INSERT INTO {table_name}(
			first_name,
			last_name,
			patronymic,
			birthday
		) VALUES(?, ?, ?, ?);""", users)
		self.conn.commit()
		cur.close()

	def selectBirthdayUsers(self, table_name='users'):
		today = date.today().strftime('%d.%m.')
		cur = self.conn.cursor()
		cur.execute(f"SELECT * FROM {table_name} WHERE birthday LIKE '{today}%'")
		data = cur.fetchall()
		cur.close()
		return data

	def __del__(self):
		self.conn.close()
		print('destructor')
