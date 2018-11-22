# Utility Functions #
def create_pairs(list1, list2):
	if len(list1) != len(list2):
		raise ValueError('Both lists must have the same length.')
	if len(list1) == 1:
		return [[list1[0], list2[0]]]
	else:
		return [[list1[0], list2[0]], *create_pairs(list1[1:], list2[1:])]

def safe_eval(arg):
	if type(arg) != str:
		return arg
	try:
		evaluated = eval(arg)
		return evaluated
	except NameError:
		return arg