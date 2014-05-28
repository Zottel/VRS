
class FORMULA:
	t = "formula"
	
	def to_cnf(self):
		raise NotImplementedError()
	
	def __invert__(self):
		if self.t == "not":
			return self.op
		else:
			return NOT(self)
	
	def __and__(self, other):
		return AND(self, other)
	
	def __or__(self, other):
		return OR(self, other)
	
	def __xor__(self, other):
		return XOR(self, other)
	
	def __lshift__(self, other):
		return IMPLIES(other, self)
	
	def __rshift__(self, other):
		return IMPLIES(self, other)

class VAR(FORMULA):
	t = "var"
	def __init__(self, name):
		self.name = name
	
	def __str__(self):
		return "%s" % (self.name)
	
	def to_cnf(self):
		return self


class UNARY(FORMULA):
	t = "unary"
	def __init__(self, op):
		if(op == None):
			raise Exception()
		self.op = op
	
	def to_cnf(self):
		raise NotImplementedError()


class NOT(UNARY):
	t = "not"
	
	def __str__(self):
		return "!%s" % (self.op)
	
	def to_cnf(self):
		if self.op.t == "var":
			return self
		elif self.op.t == "not":
			return self.op.op
		elif self.op.t == "and":
			return OR(NOT(self.op.op1), NOT(self.op.op2)).to_cnf()
		elif self.op.t == "or":
			return AND(NOT(self.op.op1), NOT(self.op.op2)).to_cnf()
		elif self.op.t == "impl":
			return (self.op.op1 & ~self.op.op2).to_cnf()
		elif self.op.t == "eq":
			return ((self.op.op1 & ~self.op.op2) | (~self.op.op1 & self.op.op2)).to_cnf()
		elif self.op.t == "xor":
			return ((self.op.op1 & self.op.op2) | (~self.op.op1 & ~self.op.op2)).to_cnf()


class BINARY(FORMULA):
	t = "binary"
	def __init__(self, op1, op2):
		if(op1 == None or op2 == None):
			raise Exception()
		self.op1 = op1
		self.op2 = op2
	
	def to_cnf(self):
		raise NotImplementedError()


class EQUIV(BINARY):
	t = "eq"
	
	def __str__(self):
		return "(%s == %s)" % (self.op1, self.op2)
	
	def to_cnf(self):
		return OR(AND(self.op1, self.op2), AND(NOT(self.op1), NOT(self.op2))).to_cnf()


class IMPLIES(BINARY):
	t = "impl"
	
	def __str__(self):
		return "(%s -> %s)" % (self.op1, self.op2)
	
	def to_cnf(self):
		return OR(NOT(self.op1), self.op2).to_cnf()


class XOR(BINARY):
	t = "xor"
	
	def __str__(self):
		return "(%s xor %s)" % (self.op1, self.op2)
	
	def to_cnf(self):
		return OR(AND(self.op1, NOT(self.op2)), AND(NOT(self.op1), self.op2)).to_cnf()


class AND(BINARY):
	t = "and"
	
	def __str__(self):
		return "(%s and %s)" % (self.op1, self.op2)
	
	def to_cnf(self):
		new1 = self.op1.to_cnf()
		new2 = self.op2.to_cnf()
		return AND(new1, new2)


class OR(BINARY):
	t = "or"
	
	def __str__(self):
		return "(%s or %s)" % (self.op1, self.op2)
	
	def to_cnf(self):
		new1 = self.op1.to_cnf()
		new2 = self.op2.to_cnf()
		
		if new1.t == "and":
			return AND(OR(new2, new1.op1).to_cnf(), OR(new2, new1.op2).to_cnf())
		
		elif new2.t == "and":
			return AND(OR(new1, new2.op1).to_cnf(), OR(new1, new2.op2).to_cnf())
		
		else:
			return OR(new1, new2)

