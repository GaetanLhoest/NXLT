###############################################################################
# test.py
#
# A simple file to test to make a compiler in python
###############################################################################
import ply.lex as lex

# List of the tokens names
tokens = (
	'VARIABLE',
	'NUMBER',
	'PLUS',
	'MINUS',
	'TIMES',
	'DIVIDE',
	'LPAREN',
	'RPAREN',
	'APP',
	'EQUAL',
	)

# Regular expression rules for simple tokens
t_PLUS		= r'\+'
t_MINUS		= r'-'
t_TIMES		= r'\*'
t_DIVIDE	= r'/'
t_LPAREN	= r'\('
t_RPAREN	= r'\)'
t_APP		= r'\''
t_EQUAL		= r'\='


t_VARIABLE	= r'[a-zA-Z_][a-zA-Z0-9_]*'

def t_NUMBER(t):
	r'\d+'
	t.value = int(t.value)
	return t

def t_newline(t):
	r'\n+'
	t.lexer.lineno += len(t.value)
	t_ignore = ' \t'

def t_error(t):
	print "Illegal character: %s" % t.value[0]
	t.lexer.skip(1)

lexer = lex.lex()

data = '''
aB45_TcnX23 = 6
x = 5
y = 7
x = x + y
'''

lexer.input(data)

while True:
	 tok = lexer.token()
	 if not tok: break
	 print tok
