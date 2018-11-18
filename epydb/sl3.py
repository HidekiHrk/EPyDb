import sqlite3

#	Error Classes #
class TableError(Exception):
	def __init__(self, string):
		self.string = string
	def __repr__(self):
		return self.string

class ColumnTypeError(Exception):
	def __init__(self, string):
		self.string = string
	def __repr__(self):
		return self.string

class Sl3:
	# Number of Connections #
	connections = 0
	def __init__(self , **kwargs):
		Sl3.connections += 1
		self.filename = kwargs.get('filename', 'data.db')
		self.__conn = sqlite3.connect(self.filename)
		self.__cursor = self.__conn.cursor()
	
	# Script to create tables easily at Will #
	def add_table(self, tablename, **kwargs):
		self.__cursor.execute(
			"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", 
			(tablename,)
		)
		supported_types = ['TEXT', 'INT']
		table_columns_string = []
		for arg in kwargs:
			argtype = kwargs.get('arg')
			if argtype.upper() in supported_types:
				table_columns_string.append('%s %s' % (arg, argtype.upper()))
				continue
			else:
				raise ColumnTypeError('Column type must be one of these ( %s ), not %s' % 
					(', '.join(supported_types), argtype)
				)
		else:
			table_columns_string = ' '.join(table_columns_string)
		if self.__cursor.fetchall()[0][0] == 0:
			self.__cursor.execute("CREATE TABLE IF NOT EXISTS %s (%s)" % (tablename, table_columns_string))
			self.__conn.commit()
			return True
		else:
			raise TableError('Table %s already exists.' % (tablename))
	
	# Removing number of instances and close database connection when deleted #
	def __del__(self):
		if Sl3.connections > 0:
			self.__conn.close()
			connections -= 1