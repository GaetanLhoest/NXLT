""" SVM - Simple Virtual Machine (or Stupid Virtual Machine)
Very simplistic virtual machine aimed to illustrate some compilers' concepts.
It probably has no other use whatsoever.

usage: svm.py <filename> 
This reads and execute the "bytecode" file given in <filename>.

SVM implements a very simplistic stack machine. It has a stack (containing only numbers) 
and a "central memory" that is adressable by names instead of adresses (think "variables"...)

The format of svm's "bytecode" is the following:
    
    each line in is the form
    tag: opcode parameter?
    
    the tag is optional; parameters depend on the opcode.
    
    Valid opcodes are:
        
        PUSHC <val>: pushes the constant (float) value <val> on the execution stack
        PUSHV <id>: pushes the value of the identifier <id> on the stack
        SET <id>: pops a value from the stack and sets <id> accordingly
        PRINT: pops a value from the stack and prints it.
        ADD, SUB, MUL, DIV: pops two values from the stack and pushes their 
                    sum, difference, product, quotient respectively.
        USUB: Changes the sign of the number on the top of the stack.
        JMP <tag>: jumps to <tag>
        JIZ, JINZ <tag>: if the top of the stack is (not) zero, jumps to <tag>
        
    Example: this would be a valid "bytecode" file to print the numbers from 0 to 9:
                    PUSHC 0.0
                    SET a
                    JMP cond1
        body1: PUSHV a
                    PRINT
                    PUSHV a
                    PUSHC 1.0
                    ADD
                    SET a
        cond1: PUSHV a
                    PUSHC 10.0
                    SUB
                    JINZ body1        
                    
    NB: whitespace is not significant in bytecode files. The identation above is for readability only.
    
    Have fun!
    
    SVM v0.2 - Matthieu Amiguet/HE-Arc, 2008
    
    CHANGES since v0.1:
    - Added some error checking when parsing the bytecode
    - Performed a few speed optimisations. The vm is almost 25% faster than v0.1
    - Added psyco optimisation if available (can be as much as 6-8x faster...)
"""

import sys
# deque are faster than lists when used as a stack:
from collections import deque 

# Let's benefit from psyco speed if available
try:
	import psyco
	psyco.full()
except ImportError:
	pass

# These are our opcodes
ops = ('PUSHC', 'PUSHV', 'SET', 
'PRINT', 
'ADD', 'SUB', 'MUL', 'DIV', 'USUB',
'JMP',
'JIZ', 'JINZ')


# Let's do some black magic to handle mnemonics as numbers...
# This is equivalent to
# PUSHC = 0
# PUSHV = 1
# ... (etc for all opcodes)
for i,o in enumerate(ops):
    setattr(sys.modules[__name__], o,i) 

# End of black magic ;-)

def parse(filename):
    ''' Parses the bytecode file and prepares it for execution.
    Some elementary error checking has been implemented, but
    it shouldn't be very difficult to make it fail... 
    Returns None is case of error'''
    
    ok = True # No errors yet
    
    # split tags from code, store them and eliminate them
    code = [line.split(':') for line in file(filename)]
    adresses = {}

    for num, line in enumerate(code):
        if len(line) == 2:
            adresses[line[0]] = num
            del line[0]

    # split opcodes from operands
    code = [line[0].split() for line in code]
    
    for line, c in enumerate(code):
        # replace mnemonics by their number
        if c[0] in ops:
            c[0] = getattr(sys.modules[__name__], c[0]) 
        else:
            print "Error: Unknown opcode %s in line %d" % (c[0], line+1) # enumerate is from 0, lines from 1...
            ok = False
        # replace strings representing numbers by the float value
        if c[0] == PUSHC:
            try:
                c[1] = float(c[1])
            except ValueError:
                print "Error: invalid constant %s in line %d" % (c[1], line+1)
                ok = False
        # replace adresses by their numeric value
        elif c[0] in [JMP,JIZ,JINZ]:
            try:
                c[1] = adresses[c[1]]
            except KeyError:
                print "Error: unknown label %s in line %d" % (c[1], line+1)
                ok = False

    # if there was an error, return None
    if not ok: code = None
    
    return code

def execute(code):
    ''' executes parsed opcode '''
    
    ip = 0 # instruction pointer
    stack = deque() # execution stack
    vars = {} # "central memory"

    # this is for speed optimization
    spop = stack.pop
    sappend = stack.append

    nb_instr = len(code)
    
    while ip < nb_instr:
        
        line = code[ip]
        mnemo = line[0]
        
        # Stack and memory manipulation
        if mnemo == PUSHC:
            sappend(line[1])
        elif mnemo == PUSHV:
                sappend(vars[line[1]])    
        elif mnemo == SET:
            vars[line[1]] = spop()
            
        # Printing
        elif mnemo == PRINT:
            print spop()
            
        # Arithmetics
        elif mnemo == ADD:
            sappend(spop()+spop())
        elif mnemo == SUB:
            val2 = spop()
            sappend(spop()-val2)
        elif mnemo == MUL:
            sappend(spop()*spop())    
        elif mnemo == DIV:
            val2 = spop()
            sappend(spop()/val2)    
        elif mnemo ==USUB:
            stack[-1] = -stack[-1]
            
        # (un)conditional jumps
        elif mnemo == JMP:
            ip = line[1]
            continue
        elif mnemo == JINZ:
            if spop():
                ip = line[1]
                continue    
        elif mnemo == JIZ:
            if not spop():
                ip = line[1]
                continue     
            
        # Fallback. Should not happen!
        else:
            print "Uknown opcode %r. Stopping here." % mnemo
            break
        

        ip += 1
    
if __name__ == '__main__':
    code = parse(sys.argv[1])
    if code:
        execute(code)