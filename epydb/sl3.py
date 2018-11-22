import sqlite3
from collections import namedtuple
from epydb.errors import *
from epydb.utils import *

class Sl3:
	# Number of Connections #
	connections = 0
	def __init__(self , **kwargs):
		Sl3.connections += 1
		self.filename = kwargs.get('filename', 'data.db')
		self.__conn = sqlite3.connect(self.filename)
		self.__cursor = self.__conn.cursor()
	
	# Script to create tables easily at Will #
	def create_table(self, tablename, **kwargs):
		ignore = kwargs.get('__ignore__')
		if type(ignore) != bool:
			ignore = False
		elif isinstance(ignore, bool):
			del kwargs['__ignore__']
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
				raise ColumnError('Column type must be one of these ( %s ), not \'%s\'' % 
					(', '.join(supported_types), argtype)
				)
		else:
			table_columns_string = ', '.join(table_columns_string)
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

	# Script to execute an sql line #
	def execute_sql(self, *args, fetch=None, commit=False):
		self.__cursor.execute(*args)
		if commit:
			self.__conn.commit()
		if fetch != None:
			if fetch.lower() in ['one', 'all']:
				result = {
					'one':lambda: self.__cursor.fetchone(),
					'all':lambda: self.__cursor.fetchall()
				}.get(fetch.lower())
				return result()
			else:
				raise ValueError('fetch must be one or all, not ' + fetch)

	# Script to delete tables #
	def del_table(self, tablename, ignore=False):
		self.__cursor.execute(
			"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?",
			(tablename,)
		)
		if self.__cursor.fetchall()[0][0] > 0:
			self.__cursor.execute("DROP TABLE %s" % tablename)
			self.__conn.commit()
		else:
			if not ignore:
				raise TableError('Table %s not exists.' % tablename)
		return self

	# List All tables in Database #
	@property
	def tables(self):
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

	# Get an table in database #
	def get_table(self, tablename):
		if type(tablename) != str:
			raise TypeError('Must be str, not %s' % type(tablename).__name__)
		tblst = self.tables
		final_table = list(filter(lambda x: x.name == tablename, tblst))
		return final_table[0] if len(final_table) >= 1 else None

	# Create Row #
	def create_row(self, tablename, data):
		if type(tablename) != str:
			raise TypeError('Must be str, not %s' % type(tablename).__name__)
		if type(data) != dict:
			raise TypeError('Must be dict, not %s' % type(data).__name__)
		basecol = data.get('basecol')
		if basecol == None:
			raise ValueError('Data needs a basecol to hash.')
		elif type(basecol) != str:
			raise TypeError('basecol must be str, not %s' % type(basecol).__name__)
		elif data.get(basecol) == None:
			raise ValueError('basecol value must be a column name.')
		del data['basecol']
		table = self.get_table(tablename)
		if table == None:
			raise TableError('Table %s not exists.' % tablename)
		tbcols = list(map(lambda x: x.name, table.cols))
		if not all(x in data for x in tbcols):
			raise ColumnError('Missing columns.')
		if any(x not in tbcols for x in data):
			raise ColumnError('Incorrect columns.')
		supported_types = [str, int, dict, set, tuple, list]
		if not all(type(data.get(x)) in supported_types for x in data):
			raise TypeError('Values must be one of these: %s' % ', '.join(map(lambda x: x.__name__, supported_types)))
		self.__cursor.execute("SELECT COUNT(*) FROM %s where %s = ?" % (tablename, basecol), (data.get(basecol),))
		if self.__cursor.fetchone()[0] >= 1:
			raise RowError('This row already exists.')
		print('INSERT INTO %s (%s) values(%s)' % (tablename, ', '.join(data),','.join(['?'] * len(data))))
		self.__cursor.execute('INSERT INTO %s (%s) values(%s)' % (tablename, ', '.join(data), ','.join(['?'] * len(data)))
			, (*list(map(lambda x: str(data.get(x)) if type(data.get(x)) != int else data.get(x), data)),)
		)
		self.__conn.commit()
		return namedtuple('row', 'values')(dict(list(map(lambda x: [x, data.get(x)], data))))

	# Get Row #
	def get_row(self, tablename, basecol, basevalue):
		supported_types = [str, int, dict, set, tuple, list]
		for x in [tablename, basecol]:
			if type(x) != str:
				raise TypeError('Must be str, not %s' % type(x).__name__)
		if type(basevalue) not in supported_types:
			raise TypeError('Must be one of these(%s), not %s' % (', '.join(map(lambda x: str(type(x).__name__), supported_types)), type(basevalue).__name__))
		table = self.get_table(tablename)
		if table == None:
			raise TableError('Table %s not exists.' % tablename)
		basevalue = str(basevalue) if type(basevalue) != int else basevalue
		tbcols = list(map(lambda x: x.name, table.cols))
		if basecol not in tbcols:
			raise ValueError('basecol value must be a column name.')
		self.__cursor.execute('SELECT COUNT(*) FROM %s WHERE %s = ?' % (tablename, basecol), (basevalue,))
		if self.__cursor.fetchone()[0] == 0:
			return None
		else:
			self.__cursor.execute('SELECT %s FROM %s WHERE %s = ?' % (', '.join(tbcols), tablename, basecol), (basevalue,))
			result = self.__cursor.fetchone()
			result = tuple(map(lambda x: safe_eval(x) if type(x) != int and type(x) == str else x, result))
			row_tuple = namedtuple('row', ' '.join(tbcols))
			return row_tuple(*result)

	# Update Row #
	def update_row(self, tablename, basecol, basevalue, data):
		supported_types = [str, int, dict, set, tuple, list]
		for x in [tablename, basecol]:
			if type(x) != str:
				raise TypeError('Must be str, not %s' % type(x).__name__)
		if type(basevalue) not in supported_types:
			raise TypeError('Must be one of these(%s), not %s' % (', '.join(map(lambda x: str(type(x).__name__), supported_types)), type(basevalue).__name__))
		if type(data) != dict:
			raise TypeError('Must be dict, not %s' % type(data).__name__)
		table = self.get_table(tablename)
		if table == None:
			raise TableError('Table %s not exists.' % tablename)
		tbcols = list(map(lambda x: x.name, table.cols))
		if basecol not in tbcols:
			raise ValueError('basecol value must be a column name.')
		if not all(x in data for x in tbcols):
			raise ColumnError('Missing columns.')
		if not all(type(data.get(x)) in supported_types for x in data):
			raise TypeError('Values must be one of these: %s' % ', '.join(map(lambda x: x.__name__, supported_types)))
		basevalue = str(basevalue) if type(basevalue) != int else basevalue
		self.__cursor.execute('SELECT COUNT(*) FROM %s WHERE %s = ?' % (tablename, basecol), (basevalue,))
		if self.__cursor.fetchone()[0] == 0:
			raise RowError('This row not exists.')
		else:
			valuestring = ', '.join(['%s = %s' % (x[0], x[1]) for x in create_pairs(list(data), len(data) * ['?'])])
			self.__cursor.execute('UPDATE %s SET %s WHERE %s = ?' % (tablename, valuestring, basecol), (*list(map(lambda x: str(x) if type(x) != int else x, data.values())), basevalue))
			self.__conn.commit()
			return self.get_row(tablename, basecol, basevalue)

	# Delete Row #
	def del_row(self, tablename, basecol, basevalue):
		supported_types = [str, int, dict, set, tuple, list]
		for x in [tablename, basecol]:
			if type(x) != str:
				raise TypeError('Must be str, not %s' % type(x).__name__)
		if type(basevalue) not in supported_types:
			raise TypeError('Must be one of these(%s), not %s' % (', '.join(map(lambda x: str(type(x).__name__), supported_types)), type(basevalue).__name__))
		table = self.get_table(tablename)
		tbcols = list(map(lambda x: x.name, table.cols))
		basevalue = str(basevalue) if type(basevalue) != int else basevalue
		if basecol not in tbcols:
			raise ValueError('basecol value must be a column name.')
		self.__cursor.execute('SELECT COUNT(*) FROM %s WHERE %s = ?' % (tablename, basecol), (basevalue,))
		if self.__cursor.fetchone()[0] == 0:
			raise RowError('This row not exists.')
		else:
			self.__cursor.execute('SELECT %s FROM %s WHERE %s = ?' % (', '.join(tbcols), tablename, basecol), (basevalue,))
			result = self.__cursor.fetchone()
			row_tuple = namedtuple('row', ' '.join(tbcols))
			self.__cursor.execute('DELETE FROM %s WHERE %s = ?' % (tablename, basecol), (basevalue,))
			self.__conn.commit()
			return row_tuple(*result)

	# Removing number of instances and close database connection when deleted #
	def __del__(self):
		if Sl3.connections > 0:
			self.__conn.close()
			Sl3.connections -= 1

if __name__ == '__main__':
	print('This is running on main file, please import from other location.')