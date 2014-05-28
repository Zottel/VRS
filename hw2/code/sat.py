import os
import sys
import subprocess
import tempfile

from sets import Set
from form import FORMULA, VAR, OR, AND

def map_variables(formula, seen, mapped, varlist):
	if formula.t == "and" or formula.t == "or":
		map_variables(formula.op1, seen, mapped, varlist)
		return map_variables(formula.op2, seen, mapped, varlist)
	elif formula.t == "not":
		return map_variables(formula.op, seen, mapped, varlist)
	elif formula.t == "var":
		if not formula.name in seen:
			seen.add(formula.name)
			
			mapped[formula.name] = len(mapped) + 1
			
			varlist.append(formula.name)
	else:
		raise NotImplementedError()

def count_clauses(formula):
	if formula.t == "and":
		return count_clauses(formula.op1) + count_clauses(formula.op2)
	elif formula.t in {"var", "or", "not"}:
		return 1
	else:
		raise NotImplementedError()

def get_clause(form, mapped_variables):
	#print("clause: %s" % form)
	if form.t == "not":
		if form.op.t == "var":
			return ["-%d" % mapped_variables[form.op.name]]
		else:
			raise NotImplementedError()
	elif form.t == "var":
		return ["%d" % mapped_variables[form.name]]
	elif form.t == "or":
		return get_clause(form.op1, mapped_variables) + get_clause(form.op2, mapped_variables)
	else:
		raise NotImplementedError()

def write_cnf(fil, form, mapped_variables):
	#print("cnf: %s" % form)
	if form.t == "and":
		write_cnf(fil, form.op1, mapped_variables)
		write_cnf(fil, form.op2, mapped_variables)
	elif form.t in ["or", "var", "not"]:
		clause = get_clause(form, mapped_variables)
		fil.write("%s 0\r\n" % " ".join(clause))

def write_dimacs(fil, form, mapped_variables):
	num_clauses = (count_clauses(form))
	
	# Problem description header
	fil.write("p cnf %d %d\r\n" % (len(mapped_variables), num_clauses))
	
	#clauses
	write_cnf(fil, form, mapped_variables)

def run_minisat(form):
	f_input = tempfile.NamedTemporaryFile(delete=False)
	f_output = tempfile.NamedTemporaryFile(delete=False)
	
	f_output.close()
	
	seen_variables = Set()
	mapped_variables = {}
	list_variables = []
	#Create a mapping of variable name => number
	map_variables(form, seen_variables, mapped_variables, list_variables)
	write_dimacs(f_input, form, mapped_variables)
	
	f_input.close()
	
	#print('running: minisat %s %s' % (f_input.name, f_output.name))
	#proc = subprocess.Popen('minisat %s %s' % (f_input.name, f_output.name), shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
	proc = subprocess.Popen('minisat %s %s' % (f_input.name, f_output.name), shell=True)
	#proc.stdin.close()
	return_code = proc.wait()
	
	f_out = open(f_output.name)
	result = f_out.read()
	
	os.unlink(f_input.name)
	os.unlink(f_output.name)
	
	if return_code == 10:
		lines = result.split('\n')
		assert lines[0] == "SAT"
		assignment = []
		for num in lines[1].split(' '):
			if num != "0":
				if num.startswith('-'):
					assignment.append(~VAR(list_variables[int(num[1:]) - 1]))
				else:
					assignment.append(VAR(list_variables[int(num) - 1]))
		return assignment
	
	elif return_code == 20:
		return None
	else:
		raise Exception()

