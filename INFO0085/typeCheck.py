# coding: latin-1

####################################################################################################
#  typeCheck.py                                                                                    #
#                                                                                                  #
# The aim of this file is to retrieve (and also infer) the type of the different variables         #
# Two passes will be done in the AST                                                               #
# The first pass  is used to retrieve the different function and variables                         #
# The second pass will be used to infer type of variable when a assignation is found               #
# Call function will also be used to check the integrity of those function (if the function call   #
# corresponds to a declared function in term of number of variables)                               #
# (There is some function which are "duplicated", cause we did it gradually                        #
#                                                                                                  #
# 2013-2014, NIX Julien & L' HOEST Gaetan                                                          #
####################################################################################################


from AST import *
from Parser import parse

####################################################################################################

# Definition of our functionData class. It will be used to store the main information we need to 
# perform variable type inference and semantic analysis in general.
# Another version of the typeCheck was ready to use the return type and return variable elements
# in order to gives the # features but as we had to incorpored it into the llvm phase, we chose 
# to let it this way
class functionData:
	
	def __init__(self, name, returnVar, nbargs, args, dictionary = {}):	
		self.name = name
		self.returnVar = returnVar
		self.nbargs = nbargs
		self.args = args
		self.dictionary = dictionary.copy()

####################################################################################################

def init():
	global compilerror      # Compiler error
	global functionDataList	# For defining function data
	global guardian
	global varline
	global scopeNumbers
	global stack
	
	functionDataList = []  	# List to contain the information for the creation of a functionData
	
	compilerror = []		# List to contain all the error 
	
	guardian = True			# A guardian in order to check if a change has been done in a functionData
	varline = []			# a list to retrieve all the lines where the variables appear
							# as we cannot retrieve those from the AST when we are done with the AST
							# and that we have to check if variables are unassigned
							
	scopeNumbers = []		# List in order to keep the last scopes we have met
	stack = []				# List to have all the variable in the previous and current scope
	



########################################################################################################
########################################################################################################
#####################################    VARIABLE RETRIEVER    #########################################
########################################################################################################
########################################################################################################


# Just call the children of the non informational Nodes
@addToClass(Node)
def varRetriever (self, lastNode):
	for c in self.children:
		c.varRetriever(c)
		
@addToClass(FunctionNode)
def varRetriever (self, lastNode):
	global functionDataList
	global compilerror
	global scopeNumbers
	global stack
	
	scopeNumbers += [0]
	
	for c in self.children:
		if c == self.children[0]: # If we are in a headNode
			listFunctionData = c.varRetriever(c) # we retrieve all the information about a headNode
			# We create the functionData object
			tmp_functionData = functionData(listFunctionData[0], listFunctionData[1], listFunctionData[2], listFunctionData[3])
			# We set the stack with the variable in the head
			stack = listFunctionData[3][:]
			# Check if two functions do not have the same name
			for i in range(0, len (functionDataList)):
				if listFunctionData[0] == functionDataList[i].name and listFunctionData[2] == functionDataList[i].nbargs:
					error = "Two functions defined with the same number of arguments at the line : " + str(self.nline)
					compilerror += [error]
			functionDataList += [tmp_functionData] # we add the functionData created in a list
			# This should be different as we wanted to define a returned variable (optional) 
			if functionDataList[-1].returnVar == "void":
				pass
			else:
				functionDataList[-1].dictionary[functionDataList[-1].returnVar] = "unassigned"
			for i in range(0,len(functionDataList[-1].args)):
				functionDataList[-1].dictionary[functionDataList[-1].args[i]] = "unassigned"
		else: # If we are in a bodyNode
			c.varRetriever(c)
	
	scopeNumbers = []
	stack = []
	return

@addToClass(HeadNode)
def varRetriever (self, lastNode):
	name = ""
	returnVar = "void"
	nbargs = 0
	args = []

	for c in self.children:
		if isinstance(self.children[0],ReturnNode): #if we have return variable for a function
			if c == self.children[0]:  # we treat the return variable 
				returnVar = c.tok
			elif c == self.children[1]: # we have the name of the function
				name += c.varRetriever(self)
			else:
				nbargs += 1
				args += [c.varRetriever(self)]
		else:
			if c == self.children[0]: # we have the name of the function
				name += c.varRetriever(self)
			else:
				nbargs += 1
				args += [c.varRetriever(self)]
				
	return [name, returnVar, nbargs, args]

@addToClass(IfNode)
def varRetriever (self, lastNode):
	global scopeNumbers
	global stack

	# We keep the scope index in the scope list
	scopeNumbers += [len(stack)]
	for c in self.children:
		c.varRetriever(c)

	# We are out of the scope, we set the list as they were before entering this scope
	stack = stack[:scopeNumbers[-1]]
	scopeNumbers = scopeNumbers[:-1]

@addToClass(WhileNode)
def varRetriever (self, lastNode):
	global scopeNumbers
	global stack
	
	# We keep the scope index in the scope list
	scopeNumbers += [len(stack)]
	for c in self.children:
		c.varRetriever(c)
		
	# We are out of the scope, we set the list as they were before entering this scope
	stack = stack[:scopeNumbers[-1]]
	scopeNumbers = scopeNumbers[:-1]

@addToClass(AssignNode)
def varRetriever (self, index):
 	global functionDataList
 	global compilerror
 	global scopeNumbers
	global stack
 		
 	# We will check if a variable is in the scape and if we have to add
 	# it into the variable stack. We only check left term of an assignation
 	name = ""
 	leftHand = self.children[0]
 	
 	if isinstance(leftHand, TokenNode):
 		name = leftHand.tok
 	elif isinstance(leftHand, array_exprNode):
 		name = leftHand.children[0]
 	
 	found = False
 	for i in range (0, len(stack)):
 		if name == stack[i]:
 			found = True
 			
 	if not found:
 		stack += [name]
 		
 	# We look for the other Nodes (tokens)
 	for c in self.children:
		c.varRetriever(c)
 		
 	
@addToClass(ParralelAssignNode)
def varRetriever (self, index):
	global functionDataList
 	global compilerror
 	global scopeNumbers
	global stack
	
	# It is the same as the assignNode but we check if the number of
	# parameters is correct.
	nbParam = 0
 	for c in self.children:
 		nbParam += 1
 	if nbParam%2 == 0:
 		for i in range(0, nbParam/2):
 			name = ""
  			leftHand = self.children[i]
  			if isinstance(leftHand, TokenNode):
		 	  name = leftHand.tok
		 	  
		 	elif isinstance(leftHand, array_exprNode):
		 		name = leftHand.children[0].tok
		 		
		 	found = False
		 	for i in range (0, len(stack)):
		 		if name == stack[i]:
		 			found = True
		 			
		 	if not found:
		 		stack += [name]
 	else:
 		error = "Error in your parallel assignment at the line : " + str(self.nline)
 		compilerror += [error]
 		return	
 	 
 	 # We look for the other Nodes (tokens)
	for c in self.children:
		c.varRetriever(c)

@addToClass(array_declNode)
def varRetriever (self, lastNode):
	global functionDataList
	global stack
 	global compilerror

 	# In order to retrieve the good name of the variable if we were in an HeadNode
 	name = self.children[0].tok
 	stack += [name]
 	if functionDataList:
 		if(lastNode, HeadNode):
 			return self.children[0].varRetriever(self)
	 	elif name in functionDataList[-1].dictionary:
				error = "Declaration arrays with the same name at the line : " + str(self.nline)
				compilerror += [error]
	return self.children[0].varRetriever(self) # array are represented in bracket

# Just to return the name of an array variable
@addToClass(array_exprNode)
def varRetriever (self, lastNode):
	global stack
 	global compilerror
 	
	name = self.children[0]
	indexNode = self.children[1]
	index = indexNode.children[0]
	
	return name
			
# We add the token in the dictionary	
# We retain the line of the variable when it appears
# We check if the variable was assign before or not
@addToClass(TokenNode)
def varRetriever (self, element):
	global functionDataList
	global compilerror
	global varline
	global scopeNumbers
	global stack
	
	varline += [ [self.tok , str(self.nline)]]
	name = self.tok
	if functionDataList:
		if isinstance(element, HeadNode):
			return name
		found = False
		for i in range(0, len(stack)):
			if name == stack[i]:
				found = True
		if not found:
			error = "Variable never assigned before at the line : " + str(self.nline)
			compilerror += [error]
		functionDataList[-1].dictionary[name] = "unassigned"
		return name
	else:
		return name

# Number are useless during this part
@addToClass(NumberNode)
def varRetriever (self, lastNode):
	return

@addToClass(Function_callNode)
def varRetriever (self, lastNode):
	for c in self.children:
		if c == self.children[0]:
			pass
		else:
			c.varRetriever(c)
			
			
			
		
########################################################################################################
########################################################################################################
#####################################    ASSIGNATION CHECK    ##########################################
########################################################################################################
########################################################################################################




# Just call the children of the non informational Nodes
@addToClass(Node)
def assignCheck (self, index):
	for c in self.children:
		c.assignCheck(index)
		
# We retrieve the index of the current function in the functionDataList from the HeadNode
@addToClass(FunctionNode)
def assignCheck (self, index):
	index = 0
	for c in self.children:
		if c == self.children[0]:
			index = c.assignCheck(index)
		else:
			c.assignCheck(index)
			
# Retrieve the index of the current function
@addToClass(HeadNode)
def assignCheck (self, index):
	global functionDataList
	
	# if # feature was implemented
	if isinstance(self.children[0],ReturnNode):
		for i in range(0, len(functionDataList)):
			if functionDataList[i].name == self.children[1].assignCheck(index):
				index = i
				return index
	else:
		for i in range(0, len(functionDataList)):
			if functionDataList[i].name == self.children[0].assignCheck(index):
				index = i
				return index
	return -1	

# Not important but was there to debug indeed
@addToClass(Function_callNode)
def assignCheck (self, index):
	return

# We check the different variables type of a assignNode
# Depending on if we have information about types or not, 
# we can infer or set an error
@addToClass(AssignNode)
def assignCheck (self, index):
 	global functionDataList
 	global guardian
 	global compilerror
 	
 	tok = ""
 	type = ""
 	
 	leftHand = self.children[0]
 	rightHand = self.children[1]
	if isinstance(leftHand, TokenNode):
		tok = leftHand.assignCheck(index)
		if functionDataList[index].dictionary[tok] == "unassigned":
			if isinstance(rightHand, OpNode):
				type = rightHand.assignCheck(index)
				if type == "unassigned":
					pass
				functionDataList[index].dictionary[tok] = type
				guardian = True
			elif isinstance(rightHand, NumberNode):
				type = rightHand.assignCheck(index)
				functionDataList[index].dictionary[tok] = type
				guardian = True
			elif isinstance(rightHand, TokenNode):
				rtok = rightHand.assignCheck(index)
				if functionDataList[index].dictionary[rtok] != "unassigned":
					functionDataList[index].dictionary[tok] = functionDataList[index].dictionary[rtok]
					guardian = True
			elif isinstance (rightHand, array_exprNode):
				rtok = rightHand.children[0].assignCheck(index)
				if functionDataList[index].dictionary[rtok] == "unassigned":
					pass
				else:
					temp = functionDataList[index].dictionary[rtok]
					functionDataList[index].dictionary[tok] = temp[1]
					guardian = True
			elif(rightHand, Function_callNode):
				nameCall = rightHand.children[0]
				callScope = 0
				for i in range(0, len(functionDataList)):
					if nameCall == functionDataList[index].name:
						callScope = i
				# the # features is not implemented
				if functionDataList[callScope].returnVar == "void":
					error = "Error assignment : assignment between void function and variable  : " + str(self.nline)
					compilerror += [error]
				elif functionDataList[callScope].returnVar == "i32":
					functionDataList[index].dictionary[tok] = "i32"
				elif functionDataList[callScope].returnVar == "double":
					functionDataList[index].dictionary[tok] = "double"
				elif functionDataList[callScope].returnVar == "i1":
					functionDataList[index].dictionary[tok] = "i1"
				else:
					functionDataList[index].dictionary[tok] = functionDataList[callScope].returnVar # if a return variable exists, we return its type
			else: 
					pass
	elif isinstance(leftHand, array_declNode):
		type = ""
		tok = leftHand.children[0].assignCheck(index)
		nbElement = leftHand.children[1].assignCheck(index)
		if functionDataList[index].dictionary[tok] == "unassigned":
		
			type = rightHand.assignCheck(index, nbElement)
			functionDataList[index].dictionary[tok] = type
			guardian = True

# Return the size of the array
@addToClass(bracketListNode)
def assignCheck (self, index):
	for c in self.children:
		if isinstance(c, NumberNode):
			return c.tok

# We check if the type are the same in the values list of an array declaration
@addToClass(ValueListNode)
def assignCheck (self, index, nbElement):
	global compilerror
	
	verification = 0
	type = ""
	
	for c in self.children:
		verification += 1
		if isinstance(c, TokenNode):
			rtok = c.assignCheck(nbElement)
			if functionDataList[index].dictionary[rtok] != "unassigned":
				if type == "":
					type = functionDataList[index].dictionary[rtok]
				elif type == functionDataList[index].dictionary[rtok]:
					type = functionDataList[index].dictionary[rtok]
				else:
					error = "Error in your Operation (not the same type) at the line : " + str(self.nline)
					compilerror += [error]
					return
		if isinstance(c, NumberNode):
			if type == "":
				type = c.assignCheck(nbElement)
			elif type == c.assignCheck(nbElement):
				type = c.assignCheck(nbElement)
			else: 
				error = "Not the same type in your array at the line : " + str(self.nline)
				compilerror += [error]
				return
	if verification == nbElement:
		return [nbElement , type]
	else:
		error = "Error, not the same number of element in your array at the line : " + str(self.nline)
		compilerror += [error]
		return

# We check if the types in the operation are the same
# Return the type 
@addToClass(OpNode)
def assignCheck (self, index):
	global functionDataList
	global compilerror
	
	type = ""

	for c in self.children:
		if isinstance(c, TokenNode):
			rtok = c.assignCheck(index)
			if functionDataList[index].dictionary[rtok] != "unassigned":
				if type == "":
					type = functionDataList[index].dictionary[rtok]
				elif type == functionDataList[index].dictionary[rtok]:
					type = functionDataList[index].dictionary[rtok]
				else:
					error = "Error in your Operation (not the same type) at the line : " + str(self.nline)
					compilerror += [error]
					return
		elif isinstance(c, NumberNode): 
			if type == "":
				type = c.assignCheck(index) 
			elif type == c.assignCheck(index):
				type = c.assignCheck(index)
			else:
				error = "Error in your Operation (not the same type) at the line : " + str(self.nline)
				compilerror += [error]
				return
		elif isinstance(c, array_exprNode):
			rtok = c.children[0].assignCheck(index)
			if functionDataList[index].dictionary[rtok] != "unassigned":
				if type == "":
					type = functionDataList[index].dictionary[rtok][1]
				elif type == functionDataList[index].dictionary[rtok][1]:
					type = functionDataList[index].dictionary[rtok][1]
				else:
					error = "Error in your Operation (not the same type) at the line : " + str(self.nline)
					compilerror += [error]
					return
	return type

# We create an assignNode between the variable in order to re-use the assignCheck method on an assignNode
@addToClass(ParralelAssignNode)
def assignCheck (self, index):
	global compilerror
	
	nbParam = 0
	leftHandParam = 0
	for c in self.children:
 		nbParam += 1
 	rightHandParam = nbParam/2
	for i in range(0, nbParam/2):
		leftTerm = self.children[leftHandParam]
		rightTerm = self.children[rightHandParam]
		# Create a new node with the two needed variables
		assign = AssignNode([leftTerm , rightTerm], self.nline)
		assign.assignCheck(index)
		leftHandParam += 1
		rightHandParam += 1
	return 

# Always return the token
@addToClass(TokenNode)
def assignCheck (self, index):
	return self.tok

# Return type, we check if there is not a function with different return type
@addToClass(OutNode)
def assignCheck (self, index):
	global compilerror
	global functionDataList
	
	typeNode = self.children[0]
	if isinstance(typeNode, TokenNode):
		tok = typeNode.assignCheck(index)
		returnType = functionDataList[index].dictionary[tok]
	else:
		returnType = typeNode.assignCheck(index)
	if returnType == "":
		pass
	elif functionDataList[index].returnVar == "void":
		functionDataList[index].returnVar = returnType
	elif functionDataList[index].returnVar != returnType:
		error = "Error in the function " + functionDataList[index].name + " at the line  : " + str(self.nline)
		compilerror += [error]
	else:
		functionDataList[index].returnVar = returnType
	for c in self.children:
		c.assignCheck(index)

# Return the type of the array
@addToClass(array_exprNode)
def assignCheck (self, index):
	rtok = self.children[0].assignCheck(index)
	if functionDataList[index].dictionary[rtok][1] == "unassigned":
		return ""
	else:
		return functionDataList[index].dictionary[rtok][1]
	
# Return the LLVM type of our numbers
@addToClass(NumberNode)
def assignCheck (self, index):
	global compilerror
	
	if type(self.tok) == int:
		return 'i32'
	elif type(self.tok) == float:
		return 'double'
	elif self.tok == 'True' or self.tok == 'False':
		return 'i1'
	else:
		error = "No Type Detected at the line : " + str(self.nline)
		compilerror += [error]
		return error
	
	
	
########################################################################################################
########################################################################################################
#######################################   FUNCTION CALL CHECK    #######################################
########################################################################################################
########################################################################################################


# Just call the children of the non informational Nodes
@addToClass(Node)
def functionCallCheck (self, currentScope):
	for c in self.children:
		c.functionCallCheck(currentScope)
 		
# Retrieve the index of the current function thanks to the HeadNode
# calls the children after (same as assignCheck
@addToClass(FunctionNode)
def functionCallCheck (self, currentScope):
	currentScope = 0
	for c in self.children:
		if c == self.children[0]:
			currentScope = c.functionCallCheck(currentScope)
		else:
			c.functionCallCheck(currentScope)
		
# Return the index of the current function	
@addToClass(HeadNode)
def functionCallCheck (self, currentScope):
	global functionDataList
	if isinstance(self.children[0], ReturnNode):
		for i in range(0, len(functionDataList)):
			if functionDataList[i].name == self.children[1].functionCallCheck(currentScope):
				currentScope = i
				return currentScope
	else:
		for i in range(0, len(functionDataList)):
			if functionDataList[i].name == self.children[0].functionCallCheck(currentScope):
				currentScope = i
				return currentScope
	return -1
			

@addToClass(Function_callNode)
def functionCallCheck (self, currentScope):
	global functionDataList
	global compilerror
	global guardian
	index = -1
	argIndex = -2
	name = self.children[0].functionCallCheck(currentScope)
	for i in range(0, len(functionDataList)):
		if functionDataList[i].name == name :
			index = i
	for c in self.children: # We could do way better, ouch
		argIndex += 1 
		if c == self.children[0]:
			pass
		elif functionDataList[index].dictionary[functionDataList[index].args[argIndex]] != "unassigned":
			pass
			if isinstance(c, NumberNode):
				if c.functionCallCheck(currentScope) != functionDataList[index].dictionary[functionDataList[index].args[argIndex]]:
					error = "Error in your function Call (bad type) at the line : " + str(self.nline)
					compilerror += [error]
			elif isinstance(c, TokenNode):
				scopeType  = functionDataList[currentScope].dictionary[c.functionCallCheck(currentScope)]
				if scopeType != "unassigned":
					if isinstance (scopeType, list):
						if isinstance (functionDataList[index].dictionary[functionDataList[index].args[argIndex]], list):
							if scopeType[1] != functionDataList[index].dictionary[functionDataList[index].args[argIndex]][1]:
								error = "Error in your function Call (bad type) at the line : " + str(self.nline)
								compilerror += [error]
						else:
							error = "Error in your function Call (bad type) at the line : " + str(self.nline)
							compilerror += [error]
					elif scopeType != functionDataList[index].dictionary[functionDataList[index].args[argIndex]]:
						error = "Error in your function Call (bad type) at the line : " + str(self.nline)
						compilerror += [error]
					elif isinstance(c, OpNode):
						type = c.assignCheck(index)
						if type == "unassigned":
							pass
						if type != functionDataList[index].dictionary[functionDataList[index].args[argIndex]]:
							error = "Error in your function Call (bad type) at the line 5: " + str(self.nline)
							compilerror += [error]
		elif isinstance(c, NumberNode):
			functionDataList[index].dictionary[functionDataList[index].args[argIndex]] = c.functionCallCheck(currentScope)
			guardian = True
		elif isinstance(c, TokenNode):
			scopeType  = functionDataList[currentScope].dictionary[c.functionCallCheck(currentScope)]
			if isinstance(scopeType, list):
				functionDataList[index].dictionary[functionDataList[index].args[argIndex]] =  scopeType
				guardian = True
			elif scopeType == "unassigned":
				pass
			else:
				functionDataList[index].dictionary[functionDataList[index].args[argIndex]] =  scopeType
				guardian = True
		elif isinstance(c, OpNode):
			type = c.assignCheck(currentScope)
			if type == "unassigned":
				pass
			functionDataList[index].dictionary[functionDataList[index].args[argIndex]] = type
			guardian = True
		elif isinstance(c, array_exprNode):
			scopeType  = functionDataList[currentScope].dictionary[c.children[0]]
			functionDataList[index].dictionary[functionDataList[index].args[argIndex]] =  scopeType
			pass
		else:
			error = "Error in your function Call (bad type) at the line : " + str(self.nline)
			compilerror += [error]
			return
	return

@addToClass(CondNode)
def functionCallCheck (self, index):
	global functionDataList
	global compilerror
	type = ""
	for c in self.children:
		if isinstance(c, CondNode):
			c.functionCallCheck(c)
		elif isinstance(c, TokenNode):
			rtok = c.assignCheck(index)
			if functionDataList[index].dictionary[rtok] != "unassigned":
				if type == "":
					type = functionDataList[index].dictionary[rtok]
				elif type == functionDataList[index].dictionary[rtok]:
					pass
				else:
					error = "Error in your Condition (not the same type) at the line : " + str(self.nline)
					compilerror += [error]
		elif isinstance(c, NumberNode): 
			if type == "":
				type = c.assignCheck(index) 
			elif type == c.assignCheck(index):
				pass
			else:
				error = "Error in your Condition (not the same type) at the line : " + str(self.nline)
				compilerror += [error]
		elif isinstance(c, array_exprNode):
			if type == "":
				type = c.assignCheck(index) 
			elif type == c.assignCheck(index):
				pass
			else:
				error = "Error in your Condition (not the same type) at the line : " + str(self.nline)
				compilerror += [error]
		elif (c, OpNode):
			type = c.assignCheck(index)
			if type == "":
				type = c.assignCheck(index) 
			elif type == c.assignCheck(index):
				pass
			else:
				error = "Error in your Condition (not the same type) at the line : " + str(self.nline)
				compilerror += [error]
		else: # Don't get fun by comparing stuff you just can't compare
			error = "Error in your Condition (bad type) at the line : " + str(self.nline)
			compilerror += [error]

@addToClass(OpNode) # same as the  assignCheck function
def functionCallCheck (self, index):
	global functionDataList
	global compilerror
	type = ""
	for c in self.children:
		if isinstance(c, TokenNode):
			rtok = c.assignCheck(index)
			if functionDataList[index].dictionary[rtok] != "unassigned":
				if type == "":
					type = functionDataList[index].dictionary[rtok]
				elif type == functionDataList[index].dictionary[rtok]:
					type = functionDataList[index].dictionary[rtok]
				else:
					error = "Error in your Operation (not the same type) at the line : " + str(self.nline)
					compilerror += [error]
					return
		elif isinstance(c, NumberNode): 
			if type == "":
				type = c.assignCheck(index) 
			elif type == c.assignCheck(index):
				type = c.assignCheck(index)
			else:
				error = "Error in your Operation (not the same type) at the line : " + str(self.nline)
				compilerror += [error]
				return
		elif isinstance(c, array_exprNode):
			rtok = c.children[0].assignCheck(index)
			if functionDataList[index].dictionary[rtok] != "unassigned":
				if type == "":
					type = functionDataList[index].dictionary[rtok][1]
				elif type == functionDataList[index].dictionary[rtok][1]:
					type = functionDataList[index].dictionary[rtok][1]
				else:
					error = "Error in your Operation (not the same type) at the line : " + str(self.nline)
					compilerror += [error]
					return
	return type

# Return the token
@addToClass(TokenNode)
def functionCallCheck (self, currentScope):
	return self.tok

# Return the LLVM type of our numbers
@addToClass(NumberNode)
def functionCallCheck (self, currentScope=0):
	global compilerror
	if type(self.tok) == int:
		return "i32"
	elif type(self.tok) == float:
		return "double"
	elif self.tok == 'True' or self.tok == 'False':
		return "i1"
	else:
		error =  "No Type Detected at the line : " + str(self.nline)
		compilerror += [error]
		return error
  
  
  
  
########################################################################################################
########################################################################################################
#########################################    TYPE CHECKING    ##########################################
########################################################################################################
########################################################################################################




# main method. Try and except in order separate the different modules
def typeCheck(ast):
	global functionDataList
	global guardian
	global compilerror
	global varline

	try:
		init()
		ast.varRetriever(ast)


		while guardian:
			
			guardian = False
			ast.assignCheck(ast)
			ast.functionCallCheck(ast)
			
		for i in range(0, len(functionDataList)):
			keys = functionDataList[i].dictionary.keys()
			for j in range(0, len(keys)):
				if functionDataList[i].dictionary[keys[j]] == "unassigned":
					error = "Assignment error :" + keys[j] + " in the function " + functionDataList[i].name +" is never assigned"
					compilerror += [error]
		for i in range(0, len(compilerror)): # because we could have no problem but at the end, still have unassigned variables
			print compilerror[i]


	except (AttributeError, TypeError) as e:
		print "Type checking went wrong, check the errors"
		for i in range(0, len(compilerror)):
			print compilerror[i]
		return
	
	return functionDataList




########################################################################################################
########################################################################################################
############################################     DEBUG    ##############################################
########################################################################################################
########################################################################################################





if __name__ == '__main__':
	import sys, os
	prog = file(sys.argv[1]).read()
	
	ast = parse(prog)
	
	init()
	ast.varRetriever(ast)
	
	while guardian:
		
		guardian = False

		ast.assignCheck(ast)
		ast.functionCallCheck(ast)
		
	for i in range(0, len(functionDataList)):
		keys = functionDataList[i].dictionary.keys()
		for j in range(0, len(keys)):
			if functionDataList[i].dictionary[keys[j]] == "unassigned":
				nline = []
				for k in range (0, len(varline)):
					if varline[k][0] == keys[j]:
						nline += varline[k][1:]
				nline = sorted(list(set(nline)))
				error = "Assignment error :" + keys[j] + " is never assigned at the line(s) : " + ', '.join(map(str, nline)) +"."
				compilerror += [error]
	for i in range(0, len(list(set(compilerror)))):
			print list(set(compilerror))[i] 	 
			
	print functionDataList[0].dictionary
	print functionDataList[1].dictionary
				


	
	
	
