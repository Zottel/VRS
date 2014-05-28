def cnf_var(v):
	return v

def cnf_not(n):
	if n.op.t == "var":
		return n
	elif n.op.t == "not":
		return cnf(n.op.op)
	elif n.op.t == "and":
		return cnf(OR(NOT(n.op.op1),NOT(n.op.op2)))
	elif n.op.t == "or":
		return cnf(AND(NOT(n.op.op1),NOT(n.op.op2)))
