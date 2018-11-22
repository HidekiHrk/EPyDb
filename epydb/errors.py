#	Error Classes #
class TableError(Exception):
	def __init__(self, string):
		self.string = string
	def __repr__(self):
		return self.string

class ColumnError(Exception):
	def __init__(self, string):
		self.string = string
	def __repr__(self):
		return self.string

class RowError(Exception):
	def __init__(self, string):
		self.string = string
	def __repr__(self):
		return self.string