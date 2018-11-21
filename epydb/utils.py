# Imports #
from epydb import sl3

# Classes #
Sl3 = sl3.Sl3

class Database:
	count = 0
	def __init__(self, type='sqlite3', filename='data.db'):
		Database.count += 1
		possible_types = {'sqlite3':Sl3}
		self.type = possible_types.get(possible_types)
		if self.type == None:
			raise ValueError('Database type must be one of these (%s), not %s' % (', '.join(possible_types), type))
		self.__db = self.type(filename=file)
	
	def create_table(self, table_name, table_info, defaultcol):
		if type(table_info) == dict:
			table_info['ignore'] = True
			table_info['#$#defaultcolumn$%#'] = 'TEXT'
		self.__db.add_table(table_name, **table_info)

	def delete_table(self, table_name)
		if type(table_info) == dict:
			table_info['ignore'] = True
		self.__db.del_table(table_name, ignore=True)

	def insert_row(self, table_name, row_name, )
	@property
	def table_list(self):
		return self.__db.list_tables()

	def __del__(self):
		if Database.count > 0:
			Database.count -= 1

if __name__ == '__main__':
	print('This is running on main file, please import from other location.')