from Parser import *
import ply.yacc as yacc
import AST
from AST import *

@addToClass(Node)
def thread (self, lastNode):
	for c in self.children:
		lastNode = c.thread(lastNode)
	lastNode.addNext(self)
	return self

@addToClass(WhileNode)
def thread(self, lastNode):
    beforeCond = lastNode
    exitCond = self.children[0].thread(lastNode)
    exitCond.addNext(self)
    exitBody = self.children[1].thread(self)
    exitBody.addNext(beforeCond.next[-1])
    return self

def thread(tree):
	entry = EntryNode()
	tree.thread(entry)
	return entry

if __name__ == '__main__':
	import sys, os
	import Parser
	prog = file(sys.argv[1]).read()
	ast = parse(prog)
	entry = thread(ast)
	
	graph = ast.makegraphicaltree()
	entry.threadTree(graph)
	
	name = os.path.splitext(sys.argv[1])[0]+'-ast-threaded.pdf'
	graph.write_pdf(name)
	print "wrote Threaded ast to", name