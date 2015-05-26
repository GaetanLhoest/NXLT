###############################################################################
# Parser.py																      #
#																			  #
# Parser.py will parser a list of Tokens and create an AST from those		  #
# use simply python Parser.pyname_of_inputfile to run the code				  #
###############################################################################

import ply.yacc as yacc
import Lexer
import AST
import os

# Get the token map
tokens = Lexer.tokens
global nlines
nlines = 1

# Define the priority of the operators
precedence = (
	('left','PLUS','MINUS'),
	('left','TIMES','DIVIDE', 'MOD'),
	('right','UMINUS'),
	)
def p_begin(p):
	'''begin		:	newlines program
					|	program'''
	if len(p) == 3:
		p[0] = p[2]
	elif len(p) == 2:
		p[0] = p[1]

def p_program(p):
	'''program		:   program  function_definition
					|   function_definition'''
		
	if len(p) == 3:
		p[0] = AST.ProgramNode(p[1].children + [AST.FunctionNode(p[2], nlines)], nlines)
	elif len(p) == 2:
		p[0] = AST.ProgramNode(AST.FunctionNode(p[1], nlines), nlines)

def p_function_definition(p):
	'''function_definition	:  head newlines LBRACE newlines body RBRACE  
							|  head LBRACE newlines body RBRACE
							|  head newlines LBRACE newlines body RBRACE  newlines
							|  head LBRACE newlines body RBRACE newlines'''
							
	if len(p) == 7 and isinstance(p[5], AST.Node):
		p[0] = [AST.HeadNode(p[1], nlines)] + [p[5]]
	elif len(p) == 6:
		p[0] = [AST.HeadNode(p[1], nlines)] + [p[4]]
	elif len(p) == 8:
		p[0] = [AST.HeadNode(p[1], nlines)] + [p[5]]
	elif len(p) == 7 and isinstance(p[4], AST.Node):
		p[0] = [AST.HeadNode(p[1], nlines)] + [p[4]]

def p_head(p):
	'''head : IDENTIFIER LPAREN argument_list RPAREN
			| IDENTIFIER HASHTAG IDENTIFIER LPAREN argument_list RPAREN
			| IDENTIFIER HASHTAG IDENTIFIER LPAREN RPAREN
			| IDENTIFIER LPAREN RPAREN'''
			
	if len(p) == 4:
		p[0] = AST.TokenNode(p[1], nlines)
	elif len(p) == 5:
		p[0] =  [AST.TokenNode(p[1], nlines)] + p[3].children
	elif len(p) == 6:
		p[0] =  [AST.ReturnNode(p[1], nlines)] + [AST.TokenNode(p[3], nlines)]
	elif len(p) == 7:
		p[0] =  [AST.ReturnNode(p[1], nlines)] + [AST.TokenNode(p[3], nlines)] + p[5].children
		
def p_argument_list(p):
	'''argument_list	 : argument_declaration
						| argument_declaration COMMA argument_list '''
						
	if len(p) == 2:
		p[0] = AST.Argument_listNode(p[1], nlines)
	elif len(p) == 4:
		p[0] = AST.Argument_listNode([p[1]] + p[3].children, nlines)
		
def p_argument_declaration(p):
    '''argument_declaration	: IDENTIFIER
							| NUMBER
							| IDENTIFIER LBRACKET RBRACKET'''
	
    if len(p) == 2:
        p[0] = AST.TokenNode(p[1], nlines)
    elif len(p) == 2 and isinstance (p[1], AST.NumberNode):
        p[0] = AST.NumberNode(p[1], nlines)
    else:
        p[0] = AST.array_declNode(AST.TokenNode(p[1], nlines), nlines)
	
def p_body(p):
	'''body	: body statement
			| statement'''
	
	if len(p) == 3:
		p[0] = AST.BodyNode(p[1].children + [p[2]], nlines)
	elif len(p) == 2:
		p[0] = AST.BodyNode(p[1], nlines)
 
		
def p_statement(p):
	'''statement	: assignment newlines
					| array_declaration newlines
					| array_assignment newlines
					| parralel_assignment newlines
					| if_block newlines
					| if_block newlines else_block newlines
					| while_block newlines
					| function_call newlines
					| print newlines
					| out newlines'''
	
	if len(p) == 3:
		p[0] = p[1]
	elif len(p) == 5:
		p[0] = [p[1]] + [p[3]]
		
def p_out(p):
	'''out	:	OUT expression'''
	
	p[0] = AST.OutNode(p[2], nlines)
		
def p_assignment(p):
	'''assignment	: IDENTIFIER EQUALS expression'''
	
	p[0] = AST.AssignNode([AST.TokenNode(p[1], nlines)] +[p[3]], nlines)

def p_multiple_assignment(p):
	'''multiple_assignment	: assignment
							| IDENTIFIER EQUALS multiple_assignment'''
							
	if len(p) == 2:
		p[0] = p[1]
	elif len(p) == 4:	
		p[0] = AST.AssignNode([AST.TokenNode(p[1], nlines)] + p[3].children, nlines)


def p_parralel_assignment(p):
	'''parralel_assignment	: parameters_list EQUALS parameters_list'''
	
	p[0] = AST.ParralelAssignNode(p[1].children+p[3].children, nlines)

def p_function_call(p):
	'''function_call	: IDENTIFIER LPAREN  RPAREN
						| IDENTIFIER LPAREN parameters_list RPAREN'''
	
	if len(p) == 4:
		p[0] = AST.Function_callNode(AST.TokenNode(p[1], nlines), nlines)
	elif len(p) == 5:
		p[0] = AST.Function_callNode([AST.TokenNode(p[1], nlines)] +  p[3].children, nlines)

def p_parameters_list(p):
	'''parameters_list	: parameter_declaration
						  | parameter_declaration COMMA parameters_list'''

	if len(p) == 2:	
		p[0] = AST.Param_listNode(p[1])
	elif len(p) == 4:
		p[0] = AST.Param_listNode([p[1]] + p[3].children, nlines)

def p_parameter_declaration(p):
	'''parameter_declaration	: expression'''
	p[0] = p[1]
	

def p_while_block(p): 
	'''while_block	 : WHILE LPAREN condition_list RPAREN LBRACE newlines body RBRACE 
					| WHILE LPAREN condition_list RPAREN newlines LBRACE newlines body RBRACE '''
					
	if len(p) == 9:
		p[0] = AST.WhileNode(p[3] , p[7], nlines)
	elif len(p) == 10:
		p[0] = AST.WhileNode(p[3] , p[8], nlines)
			  
def p_if_block(p):
	'''if_block	: IF LPAREN condition_list RPAREN LBRACE body RBRACE 
				| IF LPAREN condition_list RPAREN newlines LBRACE body RBRACE 
				| IF LPAREN condition_list RPAREN LBRACE newlines body RBRACE 
				| IF LPAREN condition_list RPAREN newlines LBRACE newlines body RBRACE '''

	if len(p) == 8:
		p[0] = AST.IfNode([p[3]] + [p[6]], nlines)
	elif len(p) == 9:
		p[0] = AST.IfNode([p[3]] + [p[7]], nlines)   
	elif len(p) == 10:
		p[0] = AST.IfNode([p[3]] + [p[8]], nlines)



def p_else_block(p):
	'''else_block : ELSE LBRACE body RBRACE 
				  | ELSE LBRACE newlines body RBRACE 
				  | ELSE newlines LBRACE body RBRACE 
				  | ELSE newlines LBRACE newlines body RBRACE '''
				  
	if len(p) == 5:
		p[0] = AST.ElseNode(p[3], nlines)
	elif len(p) == 6:
		p[0] = AST.ElseNode(p[4], nlines)
	elif len(p) == 7:
		p[0] = AST.ElseNode(p[5], nlines)
		
def p_condition_list(p):
	'''condition_list	: condition
						| condition comb_symbol condition_list'''
	 
	if len(p) == 2:
		p[0] = p[1]
	elif len(p) == 4:
		p[0] = AST.CondNode(p[2], [p[1] , p[3]], nlines)

def p_comb_symbol(p):
	'''comb_symbol	: AND
					| OR'''
	
	p[0] = AST.TokenNode(p[1])

def p_condition(p):
	'''condition	: expression comp_symbol expression'''
										
	p[0] = AST.CondNode(p[2], [p[1], p[3]], nlines)
	
def p_comp_symbol(p):
	'''comp_symbol	: LT
					| GT
					| LE
					| GE
					| EQ
					| NE'''
	
	p[0] = p[1]

def p_expression_binop(p):
	'''expression 	: expression PLUS expression
					| expression MINUS expression
					| expression TIMES expression
					| expression DIVIDE expression
					| expression MOD expression'''
				  
	p[0] = AST.OpNode(p[2], [p[1], p[3]], nlines)
	
def p_expression_uminus(p):
	'''expression : MINUS expression %prec UMINUS'''
	
	p[0] =  AST.OpNode(p[1], p[2], nlines)
	
def p_expression_number(p):
	'''expression : NUMBER'''
	
	p[0] = AST.NumberNode(p[1], nlines)
	
def p_expression_float(p):
	'''expression : FLOAT'''
	
	p[0] = AST.NumberNode(p[1], nlines)
	
def p_expression_boolean(p):
	'''expression : boolean'''
	
	p[0] = p[1]
	
def p_boolean(p):
	'''boolean	: TRUE
				| FALSE'''

	p[0] = AST.NumberNode(p[1], nlines)
	
def p_expression_name(p):
	'''expression : IDENTIFIER'''
	
	p[0] = AST.TokenNode(p[1], nlines)
	
	#try:
		##p[0] = names[p[1]]
	#except LookupError:
		#print("Undefined name '%s'" % p[1])
		##p[0] = 0

def p_exprFunction(p):
	'''expression	: IDENTIFIER LPAREN  RPAREN
					| IDENTIFIER LPAREN parameters_list RPAREN'''
	
	if len(p) == 4:
		p[0] = AST.Function_callNode(AST.TokenNode(p[1], nlines), nlines)
	elif len(p) == 5:
		p[0] = AST.Function_callNode([AST.TokenNode(p[1], nlines)] + p[3].children, nlines)

def p_exprArray(p):
	'''expression	: IDENTIFIER bracket_list
					| IDENTIFIER LBRACKET RBRACKET'''
	
	if len(p) == 3:
		p[0] = AST.array_exprNode([AST.TokenNode(p[1], nlines)] + [p[2]], nlines)
	else:
		p[0] = AST.array_exprNode([AST.TokenNode(p[1], nlines)])
			
def p_group(p):
	'''expression : LPAREN expression RPAREN'''
	p[0] = p[2]
		
def p_array_declaration(p):
	'''array_declaration	: NEW IDENTIFIER bracket_list'''
							
	p[0] = AST.array_declNode([AST.TokenNode(p[2], nlines)] + [p[3]], nlines)

def p_array_assignment(p):
	'''array_assignment	: array_declaration EQUALS value_list'''
	
	p[0] = AST.AssignNode([p[1]] + [p[3]], nlines)
 
def p_bracket_list(p):
	'''bracket_list	: LBRACKET expression RBRACKET
					| bracket_list LBRACKET expression RBRACKET'''
	  
	if len(p) == 4:
		p[0] = AST.bracketListNode(p[2], nlines)
	else:
		p[0] = AST.bracketListNode(p[1].children + [p[3]], nlines)
 
def p_value_list(p):
	'''value_list	: expression
					| value_list COMMA expression'''
	
	if len(p) == 2:
		p[0] = AST.ValueListNode(p[1], nlines)
	elif len(p) == 4:
		p[0] = AST.ValueListNode(p[1].children + [p[3]], nlines)
		
# Avoid problem with blank lines
def p_newlines(p):
	'''newlines		: NEWLINE 
					| NEWLINE newlines'''
	

	global nlines
	nlines += 1
	

def p_print(p):
	'''print		: PRINT LPAREN IDENTIFIER RPAREN'''
	
	p[0] = AST.PrintNode(AST.TokenNode(p[3], nlines), nlines)
			
# if an error occur, we are in the error recovery mode, we will discard all the token until we find the NEWLINES token to restart
# the stack. (panic mode recovery)
def p_error(p):
	if p:
		if p.type == 'NEWLINE':
			print("Syntax error :  %s aka %s is not attempt at line %s." % (p.type, "'line jump'", nlines))
		else:
			print("Syntax error :  %s aka %s is not attempt at line %s." % (p.type, str(p.value), nlines))
		while 1:
			tok = yacc.token()             # Get the next token
			if not tok or tok.type == 'NEWLINE': 
		 		break
		yacc.restart()
	else:
		print("Syntax error at EOF")

def parse(program):
	parser = yacc.yacc()
	return parser.parse(program)


##############################################DEBUG OR AST CREATION##############################################

# Build the parser and write the result as an AST graph
if __name__ == '__main__':
	import sys
	index = 0
	try:
		for i in range(1,len(sys.argv)):
			prog = file(sys.argv[i]).read()
			parser = yacc.yacc()
			print "Parsing "+sys.argv[i]+"..."
# 			try:
			result = parser.parse(prog,debug = 1)
			graph = result.makegraphicaltree()
			name = os.path.splitext(sys.argv[i])[0]+'-ast.pdf'
			graph.write_pdf(name)
			print "wrote ast to", name
# 			except (AttributeError, TypeError) as e:
# 				print "Parsing Error"
			
			index += 1
	except IOError:
		print "No such file or directory : " + sys.argv[index + 1] 

# Interpreter in command line
# 	while True:
# 		try:
# 			text = ""
# 			stopword = "stoprecording" # type this to stop recording and to see what tree you created
# 			while True:
# 				line = raw_input('calc > ')
# 				if line.strip() == stopword:
# 					break
# 				text += "%s\n" % line
# 		except EOFError:
# 			break
# 		if not text: continue
# 		parser = yacc.yacc()
# 		result = parser.parse(text)
# 		print result


