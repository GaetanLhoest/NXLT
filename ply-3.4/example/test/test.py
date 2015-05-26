###############################################################################
# test.py                                                                     #
#                                                                             #
# A simple file to test to make a compiler in python                          #
###############################################################################

import sys
import ply.lex as lex
import ply.yacc as yacc
import AST
import os

# List of the tokens names
tokens = [
	# Identifier
	'IDENTIFIER', 'NUMBER',
	
    # Operators (+,-,*,/,%,|,&,~,^,<<,>>, ||, &&, !, <, <=, >, >=, ==, !=)
    'PLUS', 'MINUS', 'UMINUS', 'TIMES', 'DIVIDE', 'MOD',
    'OR', 'AND', 'NOT', 'XOR', 'LSHIFT', 'RSHIFT',
    'LOR', 'LAND', 'LNOT',
    'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
    
    # Assignment (=, *=, /=, %=, +=, -=, <<=, >>=, &=, ^=, |=)
    'EQUALS', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL', 'PLUSEQUAL', 'MINUSEQUAL',

    # Increment/decrement (++,--)
    'PLUSPLUS', 'MINUSMINUS',
	
    # Delimeters ( ) [ ] { } , . ; :
    'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET',
    'LBRACE', 'RBRACE',
    'COMMA', 'PERIOD', 'COLON',
    'NEWLINE',
	]

# Reserved words
reserved = {
	'if' :  'IF',
	'else' : 'ELSE',
	'while' : 'WHILE',
	'continue' : 'CONTINUE',
	'break' : 'BREAK',
	'out' : 'OUT',
	'void' : 'VOID',
	}
tokens += reserved.values()

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

# Function Name definition (Identifier) except reserved ones
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*[\']*'
    if t.value in reserved:
        t.type = reserved[ t.value ]
    return t

# Numbers definition  
def t_NUMBER(t):
	r'\d+'
	t.value = int(t.value)
	return t

def t_NEWLINE(t):
	r'\n'
	t.lexer.lineno += len(t.value)
	return t

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

lexer = lex.lex()

f = open(sys.argv[1])
l = [l for l in f.readlines() if l.strip()]
f.close()
print l

# Give the lexer some input
lex.input("".join(l))

# Tokenize
while True:
    tok = lexer.token()
    if not tok: break      # No more input
    print tok
    
precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('right','UMINUS'),
    )

# dictionary of names
names = { }  

def p_program(p):
	'''program 	:   program  function_definition 
				|   function_definition '''
	
	p[0] = AST.ProgramNode(AST.FunctionNode(p[1]))
	print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
	print p[0]
	#if len(p) == 2:
		#p[0] = AST.ProgramNode(p[1])
	##elif len(p) == 3:
		##p[0] =AST.ProgramNode(p[1])
		###p[0] = p[1]
		###if not p[0]: p[0] = { }
		###if p[2]:
			###p[0] = p[2]

def p_function_definition(p):
	'''function_definition	:  head NEWLINE LBRACE NEWLINE body RBRACE NEWLINE
							|  head LBRACE NEWLINE body RBRACE NEWLINE'''
							
	p[0] = [AST.HeadNode(p[1])] + [AST.BodyNode(p[5])]
	print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
	print p[0]
	#if len(p) == 8:
		#p[0] = AST.TokenNode(p[1])
		##p[0] =AST.ProgramNode([p[1]]+p[5].children)
		##p[0] = p[5]
	##elif len(p) == 7:
		##p[0] = p[4]

def p_head(p):
	'''head : IDENTIFIER LPAREN argument_list RPAREN
			| IDENTIFIER LPAREN RPAREN'''
			
	p[0] =  [AST.TokenNode(p[1])] + [AST.Argument_listNode(p[3])]
	print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
	print p[0]
	#if len(p) == 4:
		#p[0] = AST.TokenNode(p[1])
		##p[0] = AST.TokenNode(p[3])
	##p[0] = p[3]

def p_argument_list(p):
	'''argument_list 	: argument_declaration
						| argument_declaration COMMA argument_list '''
						
	p[0] = p[1]
	#if len(p) == 2:

	#elif len(p) == 4:

	#if len(p) == 2:
		#p[0] = (p[1], None)
	#elif len(p) == 4:
		#p[0] = (p[1], p[3])
		
def p_argument_declaration(p):
	'''argument_declaration	: IDENTIFIER
							| NUMBER'''
							
	p[0] = AST.TokenNode(p[1])
	print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
	print p[0]
	#p[0] = AST.TokenNode(p[1])					
	#p[0] = p[1]
	
def p_body(p):
	'''body	: body statement
			| statement'''
				
	p[0] = p[1]
	#if len(p) == 2:

		##p[0] =AST.ProgramNode(p[
		##p[0] = (p[1], None)
	#elif len(p) == 3:
		#print 'oui'
		##p[0] =AST.ProgramNode(p[
		##p[0] = (p[1], p[2])
		
def p_statement(p):
	'''statement	: assignment NEWLINE
					| multiple_assignment NEWLINE
					| parralel_assignment NEWLINE
					| if_block 
					| if_block else_block
					| while_block NEWLINE
					| function_call NEWLINE'''
				
	#p[0] = AST.TokenNode(p[1])
	#p[0] = p[1]
	#if len(p) == 2:
		#p[0] = (p[1], None)
	#elif len(p) == 3:	
		#p[0] = (p[1], p[2])
		  
		  
def p_assignment(p):
	'''assignment	: IDENTIFIER EQUALS expression'''
	
	#p[0] = AST.TokenNode(p[1])
	#names[p[1]] = p[3]
	#p[0] = p[3]

def p_multiple_assignment(p):
	'''multiple_assignment	: assignment
							| IDENTIFIER EQUALS multiple_assignment'''
							
	#if len(p) == 2:
		#p[0] = p[1]
	#elif len(p) == 4:	
		#names[p[1]] = p[3]
		#p[0] = p[3]

def p_parralel_assignment(p):
	'''parralel_assignment	: assignment
							| IDENTIFIER COMMA parralel_assignment COMMA expression'''
							
	#if len(p) == 2:
		#p[0] = p[1]
	#elif len(p) == 6:	
		#names[p[1]] = p[5]
		#p[0] = p[3]

def p_function_call(p):
	'''function_call	: IDENTIFIER LPAREN parameters_list RPAREN 
						| IDENTIFIER EQUALS IDENTIFIER LPAREN parameters_list RPAREN'''
		
	#if len(p) == 4:
		#p[0] = p[1]
	#if len(p) == 6:
		#p[0] = p[3]

def p_parameters_list(p):
	'''parameters_list	: IDENTIFIER
						| NUMBER 
						| parameters_list COMMA IDENTIFIER
						| parameters_list COMMA NUMBER'''
						
	#if len(p) == 2:
		#p[0] = p[1]
	#if len(p) == 4:
		#p[0] = p[3]

def p_while_block(p): 
	'''while_block 	: WHILE LPAREN condition_list RPAREN LBRACE NEWLINE body RBRACE 
					| WHILE LPAREN condition_list RPAREN NEWLINE LBRACE NEWLINE body RBRACE '''
					
	#if len(p) == 8:
		#if p[3] == True:
			#p[0] = p[7]
	#elif len(p) == 9:
		#if p[3] == True:
			#p[0] = p[8]
					
def p_if_block(p):
	'''if_block	: IF LPAREN condition_list RPAREN LBRACE body RBRACE NEWLINE
				| IF LPAREN condition_list RPAREN NEWLINE LBRACE body RBRACE NEWLINE
				| IF LPAREN condition_list RPAREN LBRACE NEWLINE body RBRACE NEWLINE
				| IF LPAREN condition_list RPAREN NEWLINE LBRACE NEWLINE body RBRACE NEWLINE'''

	#if len(p) <= 9:
		#if p[3] == True:
			#p[0] = p[7]
	#elif len(p) == 10:
		#if p[3] == True:
			#p[0] = p[8]


def p_else_block(p):
	'''else_block : ELSE LBRACE body RBRACE NEWLINE
				  | ELSE LBRACE NEWLINE body RBRACE NEWLINE
				  | ELSE NEWLINE LBRACE body RBRACE NEWLINE
				  | ELSE NEWLINE LBRACE NEWLINE body RBRACE NEWLINE'''
				  
	#if len(p) == 5:
		#p[0] = p[3]
	#elif len(p) == 6:
		#p[0] = p[4]
	#elif len(p) == 7:
		#p[0] = p[5]
		
def p_condition_list(p):
	'''condition_list	: condition
						| condition comb_symbol condition_list'''
	#if len(p) == 2:
		#p[0] = p[1]
	#elif len(p) == 4:
		#if p[2] == r'&&':
			#p[0] = p[1] and p[3]
		#elif p[2] == r'\|\|':
			#p[0] = p[1] or p[3]

def p_comb_symbol(p):
	'''comb_symbol	: LAND
					| LOR'''
	#p[0] = p[1]

def p_condition(p):
	'''condition	: IDENTIFIER comp_symbol IDENTIFIER
					| IDENTIFIER comp_symbol NUMBER
					| NUMBER comp_symbol IDENTIFIER
					| NUMBER comp_symbol NUMBER'''
					
	#if p[2] == r'<'		:	p[0] = p[1] < p[3]
	#elif p[2] == r'>'	:	p[0] = p[1] > p[3]
	#elif p[2] == r'<='	:	p[0] = p[1] <= p[3]
	#elif p[2] == r'>='	:	p[0] = p[1] >= p[3]
	#elif p[2] == r'=='	:	p[0] = p[1] == p[3]
	#elif p[2] == r'!='	:	p[0] = p[1] != p[3]
	
def p_comp_symbol(p):
	'''comp_symbol	: LT
					| GT
					| LE
					| GE
					| EQ
					| NE'''
	#p[0] = p[1]

def p_expression_binop(p):
	'''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
                  
	#if p[2] == u'+'  : p[0] = p[1] + p[3]
	#elif p[2] == u'-': p[0] = p[1] - p[3]
	#elif p[2] == u'*': p[0] = p[1] * p[3]
	#elif p[2] == u'/': p[0] = p[1] / p[3]
	
def p_expression_uminus(p):
	"expression : MINUS expression %prec UMINUS"
	
	#p[0] = -p[2]
	
def p_expression_number(p):
	"expression : NUMBER"
	
	#p[0] = p[1]
	
def p_expression_name(p):
	"expression : IDENTIFIER"
	
	#try:
		##p[0] = names[p[1]]
	#except LookupError:
		#print("Undefined name '%s'" % p[1])
		##p[0] = 0

	
def p_error(p):
	if p:
		print("Syntax error at '%s'" % p.value)
	else:
		print("Syntax error at EOF")

# Build the parser
parser = yacc.yacc()

# Interpreter in command line
#while True:
#	try:
#		s = raw_input('calc > ')
#	except EOFError:
#		break
#	if not s: continue
#	result = parser.parse(s)
#	print result

# Take a non empty lines file as input
result = parser.parse("".join(l), debug = 1)

graph = result.makegraphicaltree()
name = os.path.splitext(sys.argv[1])[0]+'-ast.pdf'
graph.write_pdf(name)
print "wrote ast to", name











