from Parser import *
from threader import *
import ply.yacc as yacc
import AST
from AST import *
import operations
from operations import *

stack = []
vars = {}

def valueOfToken(t):
	if isinstance(t, str):
		try:
			return vars[t]
		except KeyError:
			print " Error: variable %s undefined" %t
	return t

def execute(node):
	while node:
		if node.__class__ in [AST.EntryNode, AST.ProgramNode]:
			pass
		elif node.__class__ == AST.TokenNode:
			stack.append(node.tok)
		elif node.__class__ == AST.NumberNode:
			stack.append(node.tok)
		elif node.__class__ == AST.PrintNode:
			val = stack.pop()
			print valueOfToken(val)
		elif node.__class__ == AST.OpNode:
			arg2 = valueOfToken(stack.pop())
			if node.nbargs == 2:
				arg1 = valueOfToken(stack.pop())
			else:
				arg1 = 0
			stack.append(operations[node.op](arg1,arg2))
		elif node.__class__ == AST.CondNode:
			arg2 = valueOfToken(stack.pop())
			if node.nbargs == 2:
				arg1 = valueOfToken(stack.pop())
			else:
				arg1 = 0
			stack.append(operations[node.op](arg1,arg2))
		elif node.__class__ == AST.AssignNode:
			val = valueOfToken(stack.pop())
			name = stack.pop()
			vars[name] = val
		elif node.__class__ == AST.WhileNode:
			cond = valueOfToken(stack.pop())
			if cond:
				node = node.next[0]
			else:
				node = node.next[1]
			continue
		
		if node.next:
			node = node.next[0]
		else:
			node = None

if __name__ == '__main__':
	import sys, os
	import Parser
	prog = file(sys.argv[1]).read()
	ast = parse(prog)
	entry = thread(ast)
	
	execute(entry)
	
	
	