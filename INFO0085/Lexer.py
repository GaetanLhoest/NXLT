###############################################################################
# Lexer.py                                                                    #
#                                                                             #
# Lexer.py is used to creates Token from an input file                        #
# use simply python Lexer.py name_of_inputfile to run the code                #
###############################################################################

import sys

import ply.lex as lex


# List of the tokens names
tokens = [
    # Identifier
    'IDENTIFIER', 'NUMBER', 'FLOAT',
    
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
    'NEWLINE', 'HASHTAG',
    
    # Generic values
    'TRUE', 'FALSE',
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
    'print' : 'PRINT',
    'new' : 'NEW',
    }

tokens += reserved.values()

# Classic operators
t_PLUS             = r'\+'
t_MINUS            = r'-'
t_TIMES            = r'\*'
t_DIVIDE           = r'/'
t_MOD              = r'%'

# Logic operators
t_OR               = r'or'
t_AND              = r'and'
t_NOT              = r'not'
t_XOR              = r'xor'

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
t_HASHTAG		   = r'\#'

# Generic values
t_TRUE			   = r'true'
t_FALSE			   = r'false'

# Function Name definition (Identifier) except reserved(token) ones
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*[\']*'
    if t.value.upper() in tokens:
        t.type = t.value.upper()
    return t

def t_FLOAT(t):
    r'-?\d+\.\d*(e-?\d+)?'
    t.value = float(t.value)
    return t

# Numbers definition  
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t
    
def t_SIMPLE_COMMENTS(t):
    r'//.*'

def t_BLOCK_COMMENTS(t):
    r'/\*(\n|.)*?(\*/)'
    t.value=t.value.count('\n')*'\n'
    t_NEWLINE(t)
    
# Count the line
def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno += len(t.value)
    return t

# Compute column. 
#     input is the input text string
#     token is a token instance
#	  used in error handling
def find_column(input,token):
    last_cr = input.rfind('\n',0,token.lexpos)
    if last_cr < 0:
	last_cr = 0
    column = (token.lexpos - last_cr) + 1
    return column   

# Error management 
def t_error(t):
    print "Illegal character: " + str(t.value[0]) + " at the line : " + str(t.lexer.lineno)
    t.lexer.skip(1)

# Completely ignored characters
t_ignore = ' \t'

lexer = lex.lex()


##############################################DEBUG##############################################

if __name__ == '__main__':
     lex.runmain()

    







