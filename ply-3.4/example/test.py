###############################################################################
# test.py                                                                     #
#                                                                             #
# A simple file to test to make a compiler in python                          #
###############################################################################

import sys
import ply.lex as lex
import ply.yacc as yacc
import AST

# Reserved words
reserved = (
	'IF', 'ELSE',
	'WHILE', 'CONTINUE', 'BREAK'
	'OUT', 'VOID',
	)

# List of the tokens names
tokens = reserved + (
	# Identifier
	'NAME', 'NUMBER',
	
    # Operators (+,-,*,/,%,|,&,~,^,<<,>>, ||, &&, !, <, <=, >, >=, ==, !=)
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
    'OR', 'AND', 'NOT', 'XOR', 'LSHIFT', 'RSHIFT',
    'LOR', 'LAND', 'LNOT',
    'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
    
    # Assignment (=, *=, /=, %=, +=, -=, <<=, >>=, &=, ^=, |=)
    'EQUALS', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL', 'PLUSEQUAL', 'MINUSEQUAL',
    'LSHIFTEQUAL','RSHIFTEQUAL', 'ANDEQUAL', 'XOREQUAL', 'OREQUAL',

    # Increment/decrement (++,--)
    'PLUSPLUS', 'MINUSMINUS',
	
    # Delimeters ( ) [ ] { } , . ; :
    'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET',
    'LBRACE', 'RBRACE',
    'COMMA', 'PERIOD', 'COLON',
	)

# Classic operators
t_PLUS             = r'\+'
t_MINUS            = r'-'
t_TIMES            = r'\*'
t_DIVIDE           = r'/'
t_MOD              = r'%'

# Logic operators
t_OR               = r'\|'
t_AND              = r'&'
t_NOT              = r'~'
t_XOR              = r'\^'

# Binary operators
t_LSHIFT           = r'<<'
t_RSHIFT           = r'>>'
t_LOR              = r'\|\|'
t_LAND             = r'&&'
t_LNOT             = r'!'

# Comparator operators
t_LT               = r'<'
t_GT               = r'>'
t_LE               = r'<='
t_GE               = r'>='
t_EQ               = r'=='
t_NE               = r'!='

# Assignment operators
t_EQUALS           = r'='
t_TIMESEQUAL       = r'\*='
t_DIVEQUAL         = r'/='
t_MODEQUAL         = r'%='
t_PLUSEQUAL        = r'\+='
t_MINUSEQUAL       = r'-='
t_LSHIFTEQUAL      = r'<<='
t_RSHIFTEQUAL      = r'>>='
t_ANDEQUAL         = r'&='
t_OREQUAL          = r'\|='
t_XOREQUAL         = r'^='

# Increment/decrement
t_PLUSPLUS         = r'\+\+'
t_MINUSMINUS       = r'--'

# Delimeters
t_LPAREN           = r'\('
t_RPAREN           = r'\)'
t_LBRACKET         = r'\['
t_RBRACKET         = r'\]'
t_LBRACE           = r'\{'
t_RBRACE           = r'\}'
t_COMMA            = r','
t_PERIOD           = r'\.'
t_COLON            = r':'

# Reserved words
reserved_map = { }
for r in reserved:
    reserved_map[r.lower()] = r

# Name definition (Identifier)
t_NAME		= r'[a-zA-Z_][a-zA-Z0-9_]*[\']*'

# Numbers definition  
def t_NUMBER(t):
	r'\d+'
	t.value = int(t.value)
	return t

# Newlines
def t_newline(t):
	r'\n+'
	t.lexer.lineno += len(t.value)

# Comments
def t_comment(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')
    
# Error management 
def t_error(t):
	print "Illegal character: %s" % t.value[0]
	t.lexer.skip(1)

# Completely ignored characters
t_ignore = ' \t'

lexer = lex.lex(optimize=1)

# Take a file as input
if __name__ == '__main__':
	lex.runmain()

precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('right','UMINUS'),
    )

# dictionary of names
names = { }

def p_statement_assign(p):
    'statement : NAME EQUALS expression'
    names[p[1]] = p[3]

def p_statement_expr(p):
    'statement : expression'
    print(p[1])
    
def p_expression_group(p):
	'expression : LPAREN expression RPAREN'
	p[0] = p[2]
	
def p_expression_binop(p):
	'''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
	if p[2] == u'+'  : p[0] = p[1] + p[3]
	elif p[2] == u'-': p[0] = p[1] - p[3]
	elif p[2] == u'*': p[0] = p[1] * p[3]
	elif p[2] == u'/': p[0] = p[1] / p[3]
	
def p_expression_uminus(p):
	"expression : MINUS expression %prec UMINUS"
	p[0] = -p[2]
	
def p_expression_number(p):
	"expression : NUMBER"
	p[0] = p[1]
	
def p_expression_name(p):
	"expression : NAME"
	try:
		p[0] = names[p[1]]
	except LookupError:
		print("Undefined name '%s'" % p[1])
		p[0] = 0

def p_error(p):
	if p:
		print("Syntax error at '%s'" % p.value)
	else:
		print("Syntax error at EOF")

# Build the parser
parser = yacc.yacc()

while True:
	try:
		s = raw_input('calc > ')
	except EOFError:
		break
	if not s: continue
	result = parser.parse(s)
	print result














