from httplib import HTTPConnection
import re

from form import VAR, AND, OR, NOT, XOR, EQUIV, IMPLIES, XOR

def sudok_rules():
	# List of form.FORMULA instances that have to hold
	# for a sudoku to be valid.
	#
	# Variable names: "<row><col><number>"
	rules = []
	
	# Iterate over all cells
	for i in range(1,10):
		# List of rows not including current one
		other_rows = range(1,10)
		other_rows.remove(i)
		
		for j in range(1,10):
			# List of columns not including current one
			other_cols = range(1,10)
			other_cols.remove(j)
			
			# At least one number per cell
			rules.append(reduce(OR, [VAR("%d%d1" % (i,j)),
			                         VAR("%d%d2" % (i,j)),
			                         VAR("%d%d3" % (i,j)),
			                         VAR("%d%d4" % (i,j)),
			                         VAR("%d%d5" % (i,j)),
			                         VAR("%d%d6" % (i,j)),
			                         VAR("%d%d7" % (i,j)),
			                         VAR("%d%d8" % (i,j)),
			                         VAR("%d%d9" % (i,j))]))
			
			# No two numbers per cell
			# (pairwise => only one number)
			for first in range(1,9):
				for second in range(first+1,10):
					rules.append(VAR("%d%d%d" % (i,j,first)) >> ~VAR("%d%d%d" % (i,j,second)))
			
			# 3x3 group members
			group3x3 = []
			for x in range(1,4):
				for y in range(1,4):
					group3x3.append("%d%d" % (x + (((i - 1) / 3) * 3), y + (((j - 1) / 3) * 3)))
			group3x3.remove("%d%d" % (i, j))
			
			# Usual rules for rows, columns and 3x3 groups
			for num in range(1,10):
				rules.append(reduce(AND, [VAR("%d%d%d" % (i,j,num)) >> ~VAR("%d%d%d" % (o,j,num)) for o in other_rows]))
				rules.append(reduce(AND, [VAR("%d%d%d" % (i,j,num)) >> ~VAR("%d%d%d" % (i,o,num)) for o in other_cols]))
				rules.append(reduce(AND, [VAR("%d%d%d" % (i,j,num)) >> ~VAR("%s%d" % (o,num)) for o in group3x3]))
	
	#for r in rules:
		#print(r)
	
	return reduce(AND, rules)

def sudok_rules_simple():
	rules = []
	
	for row in range(1, 10):
		for col in range(1, 10):
			# No two numbers per cell
			# (pairwise => only one number)
			for first in range(1,9):
				#for second in range(first+1,10):
				#	rules.append(VAR("%d%d%d" % (row,col,first)) >> ~VAR("%d%d%d" % (row,col,second)))
				others = reduce(OR, [VAR("%d%d%d" % (row, col, other)) for other in range(first+1,10)])
				rules.append(VAR("%d%d%d" % (row,col,first)) >> ~others)
	
	for row in range(1,10):
		for num in range(1,10):
			rules.append(reduce(OR, [VAR("%d%d%d" % (row, col, num)) for col in range(1,10)]))
	
	for col in range(1,10):
		for num in range(1,10):
			rules.append(reduce(OR, [VAR("%d%d%d" % (row, col, num)) for row in range(1,10)]))
	
	for group in range(0,9):
		base_row = ((group / 3) * 3) + 1
		base_col = ((group % 3) * 3) + 1
		for num in range(1,10):
			rules.append(reduce(OR, [VAR("%d%d%d" % (base_row + (field / 3), base_col + (field % 3), num)) for field in range(0,9)]))
	return reduce(AND, rules)

# Taken from https://gist.github.com/wshadow/1680c2ff7be1785c357e#file-gistfile1-py-L1
# Levels 1 to 4 are available for easy, medium, hard and evil
def get_websudoku(level = 4):
	ret = Sudoku()
	
	conn = HTTPConnection('view.websudoku.com')
	conn.request('GET', 'http://view.websudoku.com/?level=%d' % level)
	res = conn.getresponse()
	if res.status != 200:
		raise Exception("HTTP request to 'view.websudoku.com' returned status != 200\n(%d %s)" % (res.code, res.reason))
	
	res_data = res.read()
	
	values = re.search('<INPUT[^>]+ID="cheat"[^>]+VALUE="([^"]+)"', res_data).group(1)
	mask = re.search('<INPUT[^>]+ID="editmask"[^>]+VALUE="([^"]+)"', res_data).group(1)
	
	for i in range(0,81):
		ret.fields[i / 9][i % 9] = int(values[i]) if mask[i] == "0" else None
	
	#for f in fields:
	#	pass
	
	return ret

class Sudoku:
	def __init__(self, given=None):
		self.fields = [[None,None,None,None,None,None,None,None,None] for n in range(0,10)]
		
		if given != None:
			pass
	
	def parse_var(self, name):
		if self.fields[int(name[0]) - 1 ][int(name[1]) - 1] in [None, int(name[2])]:
			self.fields[int(name[0]) - 1 ][int(name[1]) - 1] = int(name[2])
		else:
			raise Exception("Feld schon belegt!: %s\n%s" % (name, self))
	
	def parse(self, form):
		while form != None:
			if form.t == "and":
				self.parse(form.op1)
				form = form.op2
			elif form.t == "not":
				if form.op.t == "var":
					form = None
				else:
					raise NotImplementedError()
			elif form.t == "var":
				self.parse_var(form.name)
				form = None
			else:
				raise NotImplementedError()
	
	def constraints(self):
		clauses = []
		for row in range(0,9):
			for column in range(0,9):
				if self.fields[row][column] != None:
					clauses.append(VAR("%d%d%d" % (row + 1, column + 1, self.fields[row][column])))
		return reduce(AND, clauses)
	
	def __str__(self):
		ret = "+---+---+---+\n"
		for l in range(0,9):
			ret = ret + ("|%s%s%s|%s%s%s|%s%s%s|\n" % tuple([(" " if x == None else x) for x in self.fields[l]]))
			
			if l % 3 == 2:
				ret = ret + "+---+---+---+\n"
		
		return ret
