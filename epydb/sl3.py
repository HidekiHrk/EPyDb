import sqlite3
from collections import namedtuple

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
		ignore = kwargs.get('ignore')
		if type(ignore) != bool:
			ignore = False
		elif isinstance(ignore, bool):
			del kwargs['ignore']
		elif ignore == None:
			ignore = False
		supported_types = ['TEXT', 'INT']
		table_columns_string = []
		if len(kwargs) == 0:
			raise TypeError('Table must have at least 1 column, but 0 were given.')
		for arg in kwargs:
			argtype = kwargs.get(arg)
			if argtype.upper() in supported_types:
				table_columns_string.append('%s %s' % (arg, argtype.upper()))
				continue
			else:
				raise ColumnTypeError('Column type must be one of these ( %s ), not \'%s\'' % 
					(', '.join(supported_types), argtype)
				)
		else:
			table_columns_string = ' '.join(table_columns_string)
		self.__cursor.execute(
			"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", 
			(tablename,)
		)
		if self.__cursor.fetchone()[0] == 0:
			self.__cursor.execute("CREATE TABLE IF NOT EXISTS %s (%s)" % (tablename, table_columns_string))
			self.__conn.commit()
		else:
			if not ignore:
				raise TableError('Table %s already exists.' % tablename)
		return self
	
	# Script to delete tables #
	def del_table(self, tablename, ignore=False):
		self.__cursor.execute(
			"SELECT COUNT(*) FROM sqlite_master WHERE type'table' AND name=?",
			(tablename,)
		)
		if self.__cursor.fetchall()[0][0] > 0:
			self.__cursor.execute("DROP TABLE %s" % tablename)
			self.__cursor.commit()
		else:
			if not ignore:
				raise TableError('Table %s not exists.' % tablename)
		return self

	#def create_row(self):

	def list_tables(self):
		self.__cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
		table_tuple = namedtuple('table', 'name cols')
		column_tuple = namedtuple('column', 'id name type notnull dvalue pk')
		table_list = tuple(map(lambda x: x[0], self.__cursor.fetchall()))
		table_tuple_list = []
		for tablename in table_list:
			self.__cursor.execute("PRAGMA table_info(%s)" % tablename)
			cols = tuple(map(lambda z: column_tuple(*z), self.__cursor.fetchall()))
			table_tuple_list.append(table_tuple(tablename, cols))
		return tuple(table_tuple_list)

	# Removing number of instances and close database connection when deleted #
	def __del__(self):
		if Sl3.connections > 0:
			self.__conn.close()
			Sl3.connections -= 1

if __name__ == '__main__':
	conct = Sl3()
	print(Sl3.connections)
	print(conct.list_tables())
	conct.add_table('hideki', opa='TEXT', ignore=True)
	print(conct.list_tables())