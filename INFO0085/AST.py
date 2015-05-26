# coding: latin-1

####################################################################################################
#  AST.py, version 0.2                                                                             #
#																								   #
# Small utility for construction, manipulation and representation								   #
# of abstract syntax trees module. Using pydot to represent a parse								   #
# tree which is sewn using graphviz (used in a special way). First,								   #
# the tree is created in a ASCII-art form and then is transformed thanks						   #
# to graphviz into a more understandable graph (in a pdf) This works,							   #
# but the arrangement is not always optimal ...													   #
#																								   #
# 2013-2014, NIX Julien & L' HOEST Gaetan, derived from initial module Matthew AMIGUET			   #																			  #
####################################################################################################

import pydot

# Principal class, creating a Node, representing a set of node (thus a tree) in a graphical way
class Node:
	count = 0 # Define the ID of a node
	type = 'Node (unspecified)' # Name of a node (and also his type)
	shape = 'ellipse'
	def __init__(self,children=None, nline = 0):
		self.nline = nline
		self.ID = str(Node.count)
		Node.count+=1
		if not children: self.children = []
		elif hasattr(children,'__len__'):
			self.children = children
		else:
			self.children = [children]
		self.next = []
	
	# Will be used in the next part of the project: Semantic
	def addNext(self,next):
		self.next.append(next)

	# method which represents a tree into an ASCII-art form tree
	def asciitree(self, prefix=''):
		result = "%s%s\n" % (prefix, repr(self))
		prefix += '|  '
		for c in self.children:
			if not isinstance(c,Node):
				result += "%s*** Error: Child of type %r: %r\n" % (prefix,type(c),c)
				continue
			result += c.asciitree(prefix)
		return result
	
	# method which returns the representation of a tree
	def __str__(self):
		return self.asciitree()
	
	# method which returns the representation of a tree
	def __repr__(self):
		return self.type
	
	# method which creates a tree in an ASCII-art form
	def makegraphicaltree(self, dot=None, edgeLabels=True):
			if not dot: dot = pydot.Dot()
			dot.add_node(pydot.Node(self.ID,label=repr(self), shape=self.shape))
			label = edgeLabels and len(self.children)-1
			for i, c in enumerate(self.children):
				c.makegraphicaltree(dot, edgeLabels)
				edge = pydot.Edge(self.ID,c.ID)
				if label:
					edge.set_label(str(i))
				dot.add_edge(edge)
				# Those two lines are there for a windows user, uncomment if you get error with pydot
				# Workaround for a bug in pydot 1.0.2 on Windows:
				# dot.set_graphviz_executables({'dot': r'C:\Program Files\Graphviz2.16\bin\dot.exe'})
			return dot
		
	# method which creates a  ride in the tree representation: used for the semantic part in order
	# to create a interpreter
	def threadTree(self, graph, seen = None, col=0):
			colors = ('red', 'green', 'blue', 'yellow', 'magenta', 'cyan')
			if not seen: seen = []
			if self in seen: return
			seen.append(self)
			new = not graph.get_node(self.ID)
			if new:
				graphnode = pydot.Node(self.ID,label=repr(self), shape=self.shape)
				graphnode.set_style('dotted')
				graph.add_node(graphnode)
			label = len(self.next)-1
			for i,c in enumerate(self.next):
				if not c: return
				col = (col + 1) % len(colors)
				color = colors[col]				
				c.threadTree(graph, seen, col)
				edge = pydot.Edge(self.ID,c.ID)
				edge.set_color(color)
				edge.set_arrowsize('.5')
				# The edges corresponding to the seams are not taken into account the layout of the graph.
				# This keeps the tree in its "standard" representation, but can cause some surprises for 
				# the ride which could seem a bit choppy... Commenting this line, the layout is much better, but 
				# the tree much less recognizable.
				edge.set_constraint('false') 
				if label:
					edge.set_taillabel(str(i))
					edge.set_labelfontcolor(color)
				graph.add_edge(edge)
			return graph	

# Definition of classes which represents intermediate Node (also non terminal symbols
	   
class ProgramNode(Node):
	type = 'Program'
	 
class FunctionNode(Node):
	type = 'function'
 
class Function_callNode(Node):
	type = 'function_call'
	
class HeadNode(Node):
	type = 'Head'

class Argument_listNode(Node):
	type = 'arg_list'

class Param_listNode(Node):
	type = 'param_list'
	
class BodyNode(Node):
	type = 'body'
	
class IfNode(Node):
	type = 'if'	

class ElseNode(Node):
	type = 'else'
	
class array_declNode(Node):
	type = 'array_decl'
	
class array_exprNode(Node):
	type = 'array_expr'

class bracketListNode(Node):
	type = 'index' 

class ValueListNode(Node):
	type = 'Value of the array elements'
	
class array_assNode(Node):
	type = 'array_ass' 

class AssignNode(Node):
	type = '='

class ParralelAssignNode(Node):
	type = '='	

class PrintNode(Node):
	type = 'print'
	
class OutNode(Node):
	type = 'out'
	
class WhileNode(Node):
	type = 'while'
	def __init__(self, cond, block, nline = 0):
		self.cond = cond
		self.block = block
		
		Node.__init__(self, [cond, block], nline)
	
class EntryNode(Node):
	type = 'ENTRY'
	def __init__(self):
		Node.__init__(self, None, 0)
		
# Definition of classes which represent leaves (also terminal symbols)
class TokenNode(Node):
	type = 'token'
	def __init__(self, tok, nline = 0):
		Node.__init__(self, None, nline)
		self.tok = tok
		
	def __repr__(self):
		return repr(self.tok)
	
class NumberNode(Node):
	type = 'number'
	def __init__(self, tok, nline = 0):
		Node.__init__(self, None, nline)
		self.tok = tok
		
	def __repr__(self):
		return repr(self.tok)

class ReturnNode(Node):
	type = 'return'
	def __init__(self, tok, nline = 0):
		Node.__init__(self, None, nline)
		self.tok = tok
		
	def __repr__(self):
		return repr(self.tok)
	
class OpNode(Node):
	def __init__(self, op, children, nline = 0):
		Node.__init__(self,children, nline)
		self.op = op
		try:
			self.nbargs = len(children)
		except AttributeError:
			self.nbargs = 1
		
	def __repr__(self):
		return "%s (%s)" % (self.op, self.nbargs)

class CondNode(Node):
	def __init__(self, op, children, nline = 0):
		Node.__init__(self,children, nline)
		self.op = op
		try:
			self.nbargs = len(children)
		except AttributeError:
			self.nbargs = 1
		
	def __repr__(self):
		return "%s (%s)" % (self.op, self.nbargs)  
	
# It is for the semantic part as we will define specific methods on specific nodes
def addToClass(cls):
# Use of a decorator to add the decorated method as a method to a class.
#	 
# Used to implement a basic form of programming oriented-object by combining different 
# methods of classes that implement the same functionality in one place.
#	 
# Beware, after using this decorator, the decorated method remains in the current namespace. 
# If it upsets can be used to destroy del. Maybe there is a way to avoid this.

	def decorator(func):
		setattr(cls,func.__name__,func)
		return func
	return decorator
