import sys

from sudoku import Sudoku, sudok_rules, sudok_rules_simple, get_websudoku

from form import VAR, NOT, AND, OR, EQUIV, XOR

from sat import run_minisat

sys.setrecursionlimit(15000)

# Rules closer to human intuition, causes about 20k clauses in the cnf
#rules = sudok_rules().to_cnf()

# Simpler rules, cause about 3k clauses
rules = sudok_rules_simple().to_cnf()


for lvl in range(1,5):
	s = get_websudoku(lvl)
	print("\n\n--------------------- LEVEL %d -----------------------" % lvl)
	print(s)
	
	assignment = reduce(AND, run_minisat(s.constraints().to_cnf() & rules))
	
	s.parse(assignment)
	print(s)


# # Show explosive nature of !(cnf == cnf).to_cnf
# rules1 = sudok_rules()
# rules2 = sudok_rules_simple()
# difference = ~(EQUIV(rules1, rules2))
# difference_cnf = difference.to_cnf() # Will probably not finish on any machine you can run this on
# print(run_minisat(difference_cnf))

