#####################################################################################################
#  llvm_translation.py																				#
#																									#
# The aim of this file is to convert our language into the llvm language							#
#																									#
# 2013-2014, NIX Julien & L' HOEST Gaetan															#
#####################################################################################################


from Parser import *
import ply.yacc as yacc
import AST
from AST import *
from typeCheck import *

# Not to be used just to give a direction
def init():
	global compilerror		# Compiler error
	global currentscope		# The current scope under compilation (for error checking)
	global varcount			# For enumerating variables in a given function
	global labelcount		# Counter for label appendix
	global wrote			# Help to know if there is yet something written in the function


	currentscope = []
	varcount = 0
	labelcount = 0
	condcount = 0
	wrote = False


# Save the llvm file
def writellvm(initialname, llvm, folder='LLVM_'):
	path = os.path.splitext(initialname)[0].split('/')
	name = path[len(path)-1]+'.s'
	outfile = open(folder+name, 'w')
	outfile.write(llvm)
	outfile.close()
	print '  * Output write to '+folder+name

@addToClass(ProgramNode)
def compile(self):
	global varcount
	str = "; LLVM generation\n"
	str += "declare ccc i32 @printf(i8*, ...)\n"
	str += "@.str = private unnamed_addr constant [4 x i8] c\"%d \\00\"\n"
	str += "@.str1 = private unnamed_addr constant [2 x i8] c\"\\0A\\00\"\n\n\n"
	str += printArray()

	index = 0
	for c in self.children:
		varcount = 1
		str += c.compile(index)
		index += 1
	return str

@addToClass(FunctionNode)
def compile(self, index):
	length = entry[index].nbargs
	dic = entry[index].dictionary
	global wrote

	if entry[index].returnVar == "void": # if the type is void, we return void
		returnType = "void"
	elif entry[index].returnVar == "i32": # if the type is void, we return void
		returnType = "i32"
	elif entry[index].returnVar == "double": # if the type is void, we return void
		returnType = "double"
	elif entry[index].returnVar == "i1": # if the type is void, we return void
		returnType = "i1"
	else:
		returnType = dic[entry[index].returnVar] # else, the variable has a type, thus we have to retrieve it from the dictionary

	wrote = False
	function =  "define fastcc " + returnType + " @" + entry[index].name + " ("

	for i in range(0, length):
		if not isinstance(dic.get(entry[index].args[i]), list):
			if i == length - 1 and dic.get(entry[index].args[i]).find('*') == -1:
				function += dic[entry[index].args[i]] +" "
				function += "%param" + entry[index].args[i]
			elif i == length - 1 and dic.get(entry[index].args[i]).find('*') != -1:
				function += dic[entry[index].args[i]] +" "
				function += "%" + entry[index].args[i]
			elif i != length - 1 and dic.get(entry[index].args[i]).find('*') == -1:
				function += dic[entry[index].args[i]] +" "
				function += "%param" + entry[index].args[i] + ", "
			elif i != length - 1 and dic.get(entry[index].args[i]).find('*') != -1:
				function += dic[entry[index].args[i]] +" "
				function += "%" + entry[index].args[i] + ", "
		else:
			if i == length - 1:
				function += "[" + str(dic[entry[index].args[i]][0]) + " x " + dic[entry[index].args[i]][1] + "]*" + " "
				function += "%" + entry[index].args[i] + " "
			else:
				function += "[" + str(dic[entry[index].args[i]][0]) + " x " + dic[entry[index].args[i]][1] + "]*" + " "
				function += "%" + entry[index].args[i] + ", "


	function += ") { \n"

	keys = dic.keys()

	for i in range(0, len(dic.keys())):
		if keys[i] not in entry[index].args: # The key is not an argument of the function
			type = dic.get(keys[i])
			if type == "float":
				type = "double"

			wrote = True
			if not isinstance(type, list):
				if type.find('*') == -1:
					function += "\t"
					function += "%" + keys[i] + " = "
					function += "alloca " + type + "\n"
		else:  # The key is an argument of the function
			type = dic.get(keys[i])
			if not isinstance(type, list):
				if type.find('*') == -1:
					if type == "float":
						type = "double"
					function += "\t%" + keys[i] + " = "
					function += "alloca " + type + "\n"
					function += "\tstore " + type + " %param" + keys[i] + ", " + type + "* %" + keys[i] + "\n"


	for c in self.children:
		if c == self.children[0]:
			pass
		else:
			function += c.compile(index)

	if returnType == "void":
		function += "\tret " + returnType + "\n"
	else:
		function += "\tret " + returnType + " -1\n"
	function += "} \n\n\n"
	return function

@addToClass(Function_callNode)
def compile(self, index):
	global varcount
	name = self.children[0].tok
	for i in range(0, len(entry)):
		if entry[i].name == name:
			callScope = i
	dic = entry[callScope].dictionary
	length = entry[callScope].nbargs



	returnType = entry[callScope].returnVar # else, the variable has a type, thus we have to retrieve it from the dictionary
	#if we had implemented the # features we should use the returnVar and returnType
	var = []
	call = ""
	for c in self.children:
		if c == self.children[0]:
			pass
		else:
			if isinstance(c, NumberNode):
				type = c.functionCallCheck(c)
				var += [type] + [str(c.tok)]
			elif isinstance(c, TokenNode):

				varname = c.tok
				type = entry[index].dictionary[varname]
				if isinstance(type, list): # We are in an array
					var += ["[" + str(type[0]) + " x " + type[1] + "]*"] + ["%" + varname]
				else:
					call += "\t%"  + str(varcount) + " = " + "load " + type + "* %" + varname + "\n"
					var += [type] + ["%" + str(varcount)]
					varcount += 1
			elif isinstance(c, OpNode):
				call += c.compile(index)
				node = c.children[0]
				if isinstance(node, NumberNode):
					type = node.functionCallCheck(0)
				elif isinstance(node, TokenNode):
					type = entry[index].dictionary[node.tok]
					if isinstance(type, list):
						type = type[1]
				var += [type] +  ["%" + str(varcount - 1)]

	call += "\tcall fastcc " + returnType + "("
	for i in range(0, length):
		if i == length - 1:
			if isinstance(dic[entry[callScope].args[i]], list):
				call += "[" + str(dic[entry[callScope].args[i]][0]) + " x " + dic[entry[callScope].args[i]][1] + "]*" + " "
			else:
				call += dic[entry[callScope].args[i]] +" "
		else:
			if isinstance(dic[entry[callScope].args[i]], list):
				call += "[" + str(dic[entry[callScope].args[i]][0]) + " x " + dic[entry[callScope].args[i]][1] + "]*" +" , "
			else:
				call += dic[entry[callScope].args[i]] +" , "
	call += ")* @" + entry[callScope].name + "("
	for i in range(0, length):
		tmpi = i*2
		if i == length - 1:
			call += str(var[tmpi] +" ")
			call += str(var[tmpi + 1])
		else:
			call += str(var[tmpi]) +" "
			call += str(var[tmpi + 1]) + " , "

	call += ")\n"
	return call

@addToClass(WhileNode)
def compile(self, index):
	global labelcount
	labelcount += 1
	locallabelcount = labelcount
	wrote = True
	condllvm = "\tbr label %while" + str(locallabelcount) + "\nwhile" + str(locallabelcount) + ":\n"
	# Writing the conditions instructions
	condllvm += self.children[0].compile(index, "while")
	condllvm += "\tbr i1 %" + str(varcount-1) + ", label %while" + str(locallabelcount) + "body, label %while" + str(locallabelcount) + "endbody\n"
	condllvm += "while" + str(locallabelcount) + "body:\n"
	# Writing the body instructions
	condllvm += self.children[1].compile(index)
	condllvm += "\tbr label %while" + str(locallabelcount) + "\n"
	condllvm += "while" + str(locallabelcount) + "endbody:\n"
	return condllvm

@addToClass(IfNode)
def compile(self, index):
	global labelcount
	labelcount += 1
	locallabelcount = labelcount
	wrote = True
	condllvm = "\tbr label %if" + str(locallabelcount) + "\nif" + str(locallabelcount) + ":\n"
	condllvm += self.children[0].compile(index, "if")
	condllvm += "\tbr i1 %" + str(varcount-1) + ", label %if" + str(locallabelcount) + "body, label %if" + str(locallabelcount) + "endbody\n"
	condllvm += "if" + str(locallabelcount) + "body:\n"
	condllvm += self.children[1].compile(index)
	condllvm += "\tbr label %if" + str(locallabelcount) + "endbody\n"
	condllvm += "if" + str(locallabelcount) + "endbody:\n"
	return condllvm


@addToClass(CondNode)
def compile(self, index, case = ""):
	global varcount
	global labelcount


	dic = entry[index].dictionary
	type = ""
	cond = ""
	operator = ""
	first = -1;
	second = -1;
	if wrote and varcount == 0:
		varcount = 1


	if str(self.op)[1:-2] == "and":
		cond += self.children[0].compile(index, case)
		cond += self.children[1].compile(index, case)
		cond += "\t%" + str(varcount) + " = and i1 %" + str(varcount-1) + ", " + str(varcount - 2) + "\n"
		varcount += 1
		cond += self.children[1].compile(index, case)
	elif str(self.op)[1:-2] == "or":
		cond += self.children[0].compile(index, case)
		cond += self.children[1].compile(index, case)
		cond += "\t%" + str(varcount) + " = or i1 %" + str(varcount-1) + ", " + str(varcount - 2) + "\n"
		varcount += 1
	else:
		for c in self.children:
			if isinstance(c, TokenNode):
				instanceTermTok = c.tok
			elif isinstance(c, array_exprNode):
				instanceTermTok = c.children[0].tok

			if isinstance(c, NumberNode):
				type = c.functionCallCheck(0)
			elif isinstance(c, CondNode):
				pass
			elif isinstance(c, OpNode):
				pass
			else:
				type = dic[instanceTermTok]

			if isinstance(c,TokenNode):
				cond += "\t%" + str(varcount) + " = load " + type + "* %" + c.tok + "\n"
				if first == -1:
					first = varcount
				else:
					second = varcount
				varcount += 1
			elif isinstance(c,NumberNode):
				cond += "\t%" + str(varcount) + " = alloca " + type + "\n"
				cond += "\tstore " + type + " " + str(c.tok).lower() + ", " + type + "* %" + str(varcount)  + "\n"
				varcount += 1
				cond += "\t%" + str(varcount) + " = load " + type + "* %" + str(varcount - 1)  + "\n"
				if first == -1:
					first = varcount
				else:
					second = varcount
				varcount += 1
			elif isinstance(c,OpNode):
				cond += c.compile(index)
				if first == -1:
					first = varcount - 1
				else:
					second = varcount - 1
			elif isinstance(c, array_exprNode):
				if str(c.children[1].children[0])[0] == "'":	#array[i]
					type2 = dic[str(c.children[1].children[0])[1:-2]]
					type3 = dic[str(c.children[0])[1:-2]]
					cond += "\t%" + str(varcount) + " = load " + type2 + "* %" + str(c.children[1].children[0])[1:-2] + "\n"
					varcount += 1
					cond += "\t%" + str(varcount) + " = sext " + type2 + " %" + str(varcount - 1) + " to i64\n"
					varcount += 1
					cond += "\t%" + str(varcount) + " = getelementptr inbounds [" + str(type3[0]) + " x " +  type[1]  + "]* %" +  str(c.children[0])[1:-2] + ", i32 0,  i64 %" + str(varcount - 1) + "\n"
					varcount += 1
					cond += "\t%" + str(varcount) + " = load " + type[1] + "* %" + str(varcount - 1) + "\n"
					if first == -1:
						first = varcount
					else:
						second = varcount
					varcount += 1
				else:	#array[4]
					type3 = dic[str(c.children[0])[1:-2]]
					index = str(c.children[1].children[0])[0:-1]
					cond += "\t%" + str(varcount) + " = alloca i32\n"
					varcount += 1
					cond += "\tstore i32 " + index + ", i32* %" + str(varcount - 1) + "\n"
					cond += "\t%" + str(varcount) + " = load i32" + "* %" + str(varcount - 1) + "\n"
					varcount += 1
					cond += "\t%" + str(varcount) + " = sext i32"  + " %" + str(varcount - 1) + " to i64\n"
					varcount += 1
					cond += "\t%" + str(varcount) + " = getelementptr inbounds [" + str(type3[0]) + " x " +  type[1]  + "]* %" +  str(c.children[0])[1:-2] + ", i32 0,  i64 %" + str(varcount - 1) + "\n"
					varcount += 1
					cond += "\t%" + str(varcount) + " = load " + type[1] + "* %" + str(varcount - 1) + "\n"
					if first == -1:
						first = varcount
					else:
						second = varcount
					varcount += 1
			elif isinstance(c, CondNode):
					cond += c.compile(index)
			else:
				print "Unknow case encountered during a condition generation"

		if self.op == "<":
			operator = " slt"
		elif self.op == ">":
			operator = " sgt"
		elif self.op == "<=":
			operator = " sle"
		elif self.op == ">=":
			operator = " gle"
		elif self.op == "==":
			operator = " eq"
		if isinstance(type, list):
			cond += "\t%" + str(varcount) + " = icmp" + operator + " " + str(type[1]) + " %" + str(first) + ", %" + str(second) + "\n"
	 	else:
			cond += "\t%" + str(varcount) + " = icmp" + operator + " " + type + " %" + str(first) + ", %" + str(second) + "\n"
	 	varcount += 1
	return cond



@addToClass(AssignNode)
def compile(self, index):
	global varcount
	dic = entry[index].dictionary
	leftTerm = self.children[0]
	rightTerm = self.children[1]

	pra = ""
	dic = entry[index].dictionary
	if isinstance(leftTerm, TokenNode):
		leftTermTok = leftTerm.assignCheck(index)
	elif isinstance(leftTerm, array_declNode):
		leftTermTok = leftTerm.children[0].tok
	elif isinstance(leftTerm, array_exprNode):
		leftTermTok = leftTerm.children[0].tok

	typeL = dic[leftTermTok]


	if varcount == 0:
		varcount = 1

	if isinstance(leftTerm, TokenNode):
		if isinstance(rightTerm,NumberNode):		# var = 4 
			typeL = rightTerm.functionCallCheck(rightTerm)
			if typeL == "double":
				value = rightTerm.tok
				value = '%.4e'% value
				print str(value)
				pra += "\tstore " + typeL + " " + str(value) + ", " + typeL + "* %" + leftTerm.compile(index)  + "\n"
			else:
				pra += "\tstore " + typeL + " " + str(rightTerm.tok).lower() + ", " + typeL + "* %" + leftTerm.compile(index)  + "\n"
		elif isinstance(rightTerm,OpNode):		# var = a + b, var = 4 + a
			pra += rightTerm.compile(index)
			pra += "\tstore " + typeL + " %" + str(varcount-1) + ", " + typeL + "* %" + leftTerm.compile(index) + "\n"
		elif isinstance(rightTerm,TokenNode):	# var = var2
			pra += "\t%" + str(varcount) + " = load " + typeL + "* %" + rightTerm.tok + "\n"
			pra += "\tstore " + typeL + " %" + str(varcount) + " , " +  typeL + "* %" + leftTerm.tok + "\n"
			varcount += 1
		elif isinstance(rightTerm, array_exprNode): # var = array[i] or var = array[4]
			if str(rightTerm.children[1].children[0])[0] == "'":	#var = array[i]
				type2 = dic[str(rightTerm.children[1].children[0])[1:-2]]
				type3 = dic[str(rightTerm.children[0])[1:-2]]
				pra += "\t%" + str(varcount) + " = load " + type2 + "* %" + str(rightTerm.children[1].children[0])[1:-2] + "\n"
				varcount += 1
				pra += "\t%" + str(varcount) + " = sext " + type2 + " %" + str(varcount - 1) + " to i64\n"
				varcount += 1
				pra += "\t%" + str(varcount) + " = getelementptr inbounds [" + str(type3[0]) + " x " +  typeL  + "]* %" +  str(rightTerm.children[0])[1:-2] + ", i32 0,  i64 %" + str(varcount - 1) + "\n"
				varcount += 1
				pra += "\t%" + str(varcount) + " = load " + typeL + "* %" + str(varcount - 1) + "\n"
				pra += "\tstore " + typeL + " %" + str(varcount) + " , " +  typeL + "* %" + leftTerm.tok + "\n"
				varcount += 1
			else:	#var = array[4]
				type3 = dic[str(rightTerm.children[0])[1:-2]]
				index = str(rightTerm.children[1].children[0])[0:-1]
				pra += "\t%" + str(varcount) + " = alloca i32\n"
				varcount += 1
				pra += "\tstore i32 " + index + ", i32* %" + str(varcount - 1) + "\n"
				pra += "\t%" + str(varcount) + " = load i32" + "* %" + str(varcount - 1) + "\n"
				varcount += 1
				pra += "\t%" + str(varcount) + " = sext i32"  + " %" + str(varcount - 1) + " to i64\n"
				varcount += 1
				pra += "\t%" + str(varcount) + " = getelementptr inbounds [" + str(type3[0]) + " x " +  typeL  + "]* %" +  str(rightTerm.children[0])[1:-2] + ", i32 0,  i64 %" + str(varcount - 1) + "\n"
				varcount += 1
				pra += "\t%" + str(varcount) + " = load " + typeL + "* %" + str(varcount - 1) + "\n"
				pra += "\tstore " + typeL + " %" + str(varcount) + " , " +  typeL + "* %" + leftTerm.tok + "\n"
				varcount += 1
		elif isinstance(rightTerm, Function_callNode):
			pra += "\t%" + str(varcount) + " = " + rightTerm.compile(index)
			varcount += 1
			pra += "\tstore " + typeL + " %" + str(varcount - 1) + " , " +  typeL + "* %" + leftTerm.tok + "\n"
	elif isinstance(leftTerm, array_exprNode):
		if str(leftTerm.children[1].children[0])[0] == "'": # array[i] =
			type2 = dic[str(leftTerm.children[1].children[0])[1:-2]]
			type3 = dic[str(leftTerm.children[0])[1:-2]]
			pra += "\t%" + str(varcount) + " = load i32* %" + str(leftTerm.children[1].children[0])[1:-2] + "\n"
			varcount += 1
			pra += "\t%" + str(varcount) + " = sext i32 %" + str(varcount - 1) + " to i64\n"
			varcount += 1
			pra += "\t%" + str(varcount) + " = getelementptr inbounds [" + str(typeL[0]) + " x " + str(typeL[1]) + "]* %" + leftTermTok + ", i32 0, i64 %" + str(varcount - 1) + "\n"
			first = varcount
			varcount += 1
		else: # array[4] =
			pra += "\t%" + str(varcount) + " = alloca i32\n"
			pra += "\tstore i32 " + str(leftTerm.children[1].children[0]) + ", i32* %" + str(varcount) + "\n"
			varcount += 1
			pra += "\tload i32* %" + str(varcount - 1) + "\n"
			pra += "\t%" + str(varcount) + " = sext i32 %" + str(varcount - 1) + " to i64\n"
			varcount += 1
			pra += "\t%" + str(varcount) + " = getelementptr inbounds [" + str(typeL[0]) + " x " +  str(typeL[1])  + "]* %" +  str(leftTerm.children[0])[1:-2] + ", i32 0,  i64 %" + str(varcount - 1) + "\n"
			first = varcount
			varcount += 1

		if isinstance(rightTerm,NumberNode):		# Example: array[i]  = 4
			pra += "\tstore " + str(typeL[1]) + " " + str(rightTerm.tok) + ", " + str(typeL[1]) + "* %" + str(varcount - 1)  + "\n"
		elif isinstance(rightTerm,OpNode):		# Example: array[i] = a + b, var = 4 + a
			pra += rightTerm.compile(index)
			pra += "\tstore " + typeL + " %" + str(varcount-1) + ", " + typeL + "* %" + leftTerm.compile(index) + "\n"
		elif isinstance(rightTerm,TokenNode):  # array[i] = var
			pra += "\t%" + str(varcount) + " = load " + str(typeL[1]) + "* %" + rightTerm.tok + "\n"
			pra += "\tstore " + str(typeL[1]) + " %" + str(varcount) + " , " +  str(typeL[1]) + "* %" + str(varcount - 1) + "\n"
			varcount += 1
		elif isinstance(rightTerm, array_exprNode): # a faire
			if str(rightTerm.children[1].children[0])[0] == "'":	#array[i] = array[j]
				rightTermTok = rightTerm.children[0].tok
				typeR = dic[rightTermTok]
				type2 = dic[str(rightTerm.children[1].children[0])[1:-2]]
				pra += "\t%" + str(varcount) + " = load " + type2 + "* %" + str(rightTerm.children[1].children[0])[1:-2] + "\n"
				varcount += 1
				pra += "\t%" + str(varcount) + " = sext " + type2 + " %" + str(varcount - 1) + " to i64\n"
				varcount += 1
				pra += "\t%" + str(varcount) + " = getelementptr inbounds [" + str(typeR[0]) + " x " +  str(typeR[1])  + "]* %" +  str(rightTerm.children[0])[1:-2] + ", i32 0,  i64 %" + str(varcount - 1) + "\n"
				varcount += 1
				pra += "\t%" + str(varcount) + " = load " + str(typeR[1]) + "* %" + str(varcount - 1) + "\n"
				pra += "\tstore " + str(typeR[1]) + " %" + str(varcount) + " , " +  str(typeR[1]) + "* %" + str(varcount - 4) + "\n"
				varcount += 1
			else:	#array[i] = array[4]
				rightTermTok = rightTerm.children[0].tok
				typeR = dic[rightTermTok]
				index = str(rightTerm.children[1].children[0])[0:-1]
				pra += "\t%" + str(varcount) + " = alloca i32\n"
				varcount += 1
				pra += "\tstore i32 " + index + ", i32* %" + str(varcount - 1) + "\n"
				pra += "\t%" + str(varcount) + " = load i32" + "* %" + str(varcount - 1) + "\n"
				varcount += 1
				pra += "\t%" + str(varcount) + " = sext i32"  + " %" + str(varcount - 1) + " to i64\n"
				varcount += 1
				pra += "\t%" + str(varcount) + " = getelementptr inbounds [" + str(typeR[0]) + " x " +  str(typeR[1])  + "]* %" +  str(rightTerm.children[0])[1:-2] + ", i32 0,  i64 %" + str(varcount - 1) + "\n"
				varcount += 1
				pra += "\t%" + str(varcount) + " = load " + str(typeR[1]) + "* %" + str(varcount - 1) + "\n"
				pra += "\tstore " + str(typeR[1]) + " %" + str(varcount) + " , " +  str(typeL[1]) + "* %" + str(first) + "\n"
				varcount += 1
		elif isinstance(rightTerm, Function_callNode):
			pra += "\t%" + str(varcount) + " = " + rightTerm.compile(index)
			varcount += 1
			pra += "\tstore " + typeL + " %" + str(varcount - 1) + " , " +  typeL + "* %" + str(varcount - 2) + "\n"
		else:
			print "Encountered unknow case"



	elif isinstance(leftTerm, array_declNode):
		name = leftTerm.children[0].tok
		size = typeL[0]
		typeL = typeL[1]
		if isinstance(rightTerm, ValueListNode):
			pra += "\t%" + name + " = alloca [" + str(size) + " x " + typeL + "], align 16\n"
			for i in range(0,size):
				pra += "\t%" + str(varcount) + " = getelementptr inbounds [" + str(size) + " x " + typeL + "]*" + " %" +  name + ", i32 0,  i64 " + str(i) + "\n"
				pra += "\tstore " + typeL + " " + str(rightTerm.children[i])[:-1] + ", " + typeL + "* %" + str(varcount) +  "\n"
				varcount += 1

	return pra

@addToClass(OpNode)
def compile(self, index):
	global varcount

	first = -1; # First member of the operation
	second = -1; # Second member of the operation
	dic = entry[index].dictionary

	operator = ""
	op = ""
	type = ""



	for c in self.children:
		if isinstance(c, NumberNode):
			type = c.functionCallCheck(0)
			op += "\t%" + str(varcount) + " = alloca " + type + "\n"
			op += "\tstore " + type + " " + str(c.tok) + ", " + type + "* %" + str(varcount)  + "\n"
			varcount += 1
			op += "\t%" + str(varcount) + " = load " + type + "* %" + str(varcount - 1)  + "\n"
			if first == -1:
				first = varcount
			else:
				second = varcount
			varcount += 1
		elif isinstance(c , OpNode):
			op += c.compile(index)
			first = varcount - 1
			second = varcount - 3
		elif isinstance(c , TokenNode):
			type = dic[c.tok]
			op += "\t%" + str(varcount) + " = load " + type + "* %" + c.tok + "\n"
			if first == -1:
				first = varcount
			else:
				second = varcount
			varcount += 1
		elif isinstance(c , array_exprNode):
			instanceTok = c.children[0].tok
			type = dic[instanceTok]
			if str(c.children[1].children[0])[0] == "'": # array[i]
				op += "\t%" + str(varcount) + " = load i32* %" + str(c.children[1].children[0])[1:-2] + "\n"
				varcount += 1
				op += "\t%" + str(varcount) + " = sext i32 %" + str(varcount - 1) + " to i64\n"
				varcount += 1
				op += "\t%" + str(varcount) + " = getelementptr inbounds [" + str(type[0]) + " x " + str(type[1]) + "]* %" + instanceTok + ", i32 0, i64 %" + str(varcount - 1) + "\n"
				varcount += 1
				op += "\t%" + str(varcount) + " = load " + str(type[1]) + "* %" + str(varcount - 1) + "\n"
				if first == -1:
					first = varcount
				else:
					second = varcount
				varcount += 1
			else: # array[4]
				op += "\t%" + str(varcount) + " = alloca i32\n"
				op += "\tstore i32 " + str(c.children[1].children[0])[:-1] + ", i32* %" + str(varcount) + "\n"
				varcount += 1
				op += "\tload i32* %" + str(varcount - 1) + "\n"
				varcount += 1
				op += "\t%" + str(varcount) + " = sext i32 %" + str(varcount - 1) + " to i64\n"
				varcount += 1
				op += "\t%" + str(varcount) + " = getelementptr inbounds [" + str(type[0]) + " x " +  str(type[1])  + "]* %" +  str(c.children[0])[1:-2] + ", i32 0,  i64 %" + str(varcount - 1) + "\n"
				varcount += 1
				op += "\t%" + str(varcount) + " = load " + str(type[1]) + "* %" + str(varcount - 1) + "\n"
				if first == -1:
					first = varcount
				else:
					second = varcount
				varcount += 1
			type = type[1]
		elif isinstance(c , Function_callNode):
			op += c.compile(index)
			if first == -1:
				first = varcount
			else:
				second = varcount
			varcount += 1
		else:
			print "Unknow case encoutered during an operation"
			
	if type == "i32":
		if self.op == "+":
			operator = "add"
		elif self.op == "-":
			operator = "sub"
		elif self.op == "*":
			operator = "mul"
		elif self.op == "/":
			operator = "sdiv"
		elif self.op == "%":
			operator = "srem"
	elif type == "double":
		if self.op == "+":
			operator = "fadd"
		elif self.op == "-":
			operator = "fsub"
		elif self.op == "*":
			operator = "fmul"
		elif self.op == "/":
			operator = "fdiv"
		elif self.op == "%":
			operator = "frem"


	op += "\t%" + str(varcount) + " = " + operator + " " + type + " %" + str(first) + ", %" + str(second) + "\n"
	varcount += 1

	return op

@addToClass(ParralelAssignNode)
def compile (self, index):
	global compilerror
	ppl = ""
	nbParam = 0
	leftHandParam = 0
	for c in self.children:
		nbParam += 1
	rightHandParam = nbParam/2
	if nbParam%2 == 0:
		for i in range(0, nbParam/2):
			leftTerm = self.children[leftHandParam]
			rightTerm = self.children[rightHandParam]
			assign = AssignNode([leftTerm , rightTerm], self.nline)
			ppl += assign.compile(index)
			leftHandParam += 1
			rightHandParam += 1
	return ppl

@addToClass(array_exprNode)
def compile(self, index):
	global varcount
	dic = entry[index].dictionary
	selfTok = self.children[0].tok
	are = ""

	typeS = dic[selfTok]

	if str(self.children[1].children[0])[0] == "'": # array[i] =
		are += "\t%" + str(varcount) + " = load i32* %" + str(self.children[1].children[0])[1:-2] + "\n"
		varcount += 1
		are += "\t%" + str(varcount) + " = sext i32 %" + str(varcount - 1) + " to i64\n"
		varcount += 1
		are += "\t%" + str(varcount) + " = getelementptr inbounds [" + str(typeS[0]) + " x " + str(typeS[1]) + "]* %" + selfTok + ", i32 0, i64 %" + str(varcount - 1) + "\n"
		varcount += 1
	else: # array[4] =
		are += "\t%" + str(varcount) + " = alloca i32\n"
		are += "\tstore i32 " + str(self.children[1].children[0])[:-1] + ", i32* %" + str(varcount) + "\n"
		varcount += 1
		are += "\tload i32* %" + str(varcount - 1) + "\n"
		varcount += 1
		are += "\t%" + str(varcount) + " = sext i32 %" + str(varcount - 1) + " to i64\n"
		varcount += 1
		are += "\t%" + str(varcount) + " = getelementptr inbounds [" + str(typeS[0]) + " x " +  str(typeS[1])  + "]* %" +  str(self.children[0])[1:-2] + ", i32 0,  i64 %" + str(varcount - 1) + "\n"
		varcount += 1

	return are

@addToClass(TokenNode)
def compile(self, index):
	return self.tok

@addToClass(PrintNode)
def compile(self, index):
	global varcount
	pex = ""
	dic = entry[index].dictionary
	tok = str(self.children[0])[1:-2]
	type = dic.get(tok)
	if not isinstance(type, list):
		pex += "\t%" + str(varcount) + " = load " + type + "* %" + self.children[0].tok + "\n"
		pex += "\tcall i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([4 x i8]* @.str, i32 0, i32 0), i32 %" + str(varcount) + ")\n"
		pex += "\tcall i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([2 x i8]* @.str1, i32 0, i32 0))\n"
		varcount += 3
	elif isinstance(type, list):
		pex += "\t%" + str(varcount) + " = getelementptr inbounds [" + str(type[0]) + " x " + str(type[1]) + "]* %" + tok + ", i64 0, i64 0\n"
		pex += "\tcall fastcc void (i32*, i32)* @printArray(i32* %" + str(varcount) + ", i32 " + str(type[0]) + ")\n"
		varcount += 1
	else:
		print "Unknow case encountered during printing"

	return pex

@addToClass(OutNode)
def compile(self, index):
	global varcount
	dic = entry[index].dictionary
	out = ""

	if isinstance(self.children[0], TokenNode):
		token = self.children[0].assignCheck(index)
		type = dic[token]
		out += "\t%" + str(varcount) + " = load " + type + "* %" + token + "\n"
		out += "\tret " + type + " %" + str(varcount) + "\n"
		varcount += 1
	elif isinstance(self.children[0], NumberNode):
		token = self.children[0].tok
		type = self.children[0].functionCallCheck(token)
		out += "\tret " + type + " " + str(token).lower() + "\n"
		varcount += 1
	elif isinstance(self.children[0], array_exprNode):
		token = self.children[0].children[0].tok
		type = dic[token]
		out += self.children[0].compile(index)
		out += "\t%" + str(varcount) + " = load " + str(type[1]) + "* %" + str(varcount - 1) + "\n"
		varcount += 1
		out += "\tret " + str(type[1]) + " %" + str(varcount - 1) + "\n"
	elif isinstance(self.children[0], OpNode):
		out += self.children[0].compile(index)
	

	return out

@addToClass(Node)
def compile(self, index):
	node = ""
	for c in self.children:
		if isinstance(c, TokenNode):
			pass
		else:
			node += c.compile(index)
	return node

def printArray():
	pra = ""
	pra += "define fastcc void @printArray(i32* %array, i32 %len){\n"
	pra += "entry:\n"
	pra += "\t%l = icmp ugt i32 %len, 0\n"
	pra += "\tbr i1 %l, label %loop, label %endLoop\n"
	pra += "loop:\n"
	pra += "\t%i = phi i32 [ %i.next, %loop], [ 0, %entry ]\n"
	pra += "\t%k = getelementptr inbounds i32* %array, i32 %i\n"
	pra += "\t%value = load i32* %k, align 4\n"
	pra += "\tcall i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([4 x i8]* @.str, i32 0, i32 0), i32 %value)\n"
	pra += "\t%i.next = add i32 %i, 1\n"
	pra += "%exitCond = icmp eq i32 %i.next, %len\n"
	pra += "\tbr i1 %exitCond, label %endLoop, label %loop\n"
	pra += "\tendLoop:\n"
	pra += "\tcall i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([2 x i8]* @.str1, i32 0, i32 0))\n"
	pra += "\tret void\n"
	pra += "}\n\n"
	return pra


if __name__ == '__main__':
	import sys, os
	import Parser

	global compilerror

	if len(sys.argv) < 2 or sys.argv[1]=='*.s': print ' * Nothing to compile'

	try:
		for i in range(1,len(sys.argv)):
			if os.path.exists(sys.argv[i]):
				prog = file(sys.argv[i]).read()
				ast = parse(prog)
				entry = typeCheck(ast)

				init()
				try:
					if isinstance(ast, Node):
						compiled = ""
						# Compile the AST node
						compiled += ast.compile()
						writellvm(sys.argv[i], compiled)
				except TypeError:
					print "llvm translation went wrong, check the errors"

	except (KeyboardInterrupt, SystemExit):
		pass

# 	Command line interpreter
# 	try:
# 		for i in range(1,len(sys.argv)):
# 			if os.path.exists(sys.argv[i]):
# 				prog = file(sys.argv[i]).read()
# 
# 			while True:
# 				try:
# 					text = ""
# 					stopword = "stoprecording" # type this to stop recording and to see what tree you created
# 					while True:
# 						line = raw_input('calc > ')
# 						if line.strip() == stopword:
# 							break
# 						text += "%s\n" % line
# 				except EOFError:
# 					break
# 				if not text: continue
# 				parser = yacc.yacc()
# 				ast = parser.parse(text)
# 				entry = typeCheck(ast)
# 
# 				init()
# 				try:
# 					if isinstance(ast, Node):
# 						compiled = ""
# 						# Compile the AST node
# 						compiled += ast.compile()
# 						writellvm(sys.argv[i], compiled)
# 				except TypeError:
# 					print "llvm translation went wrong, check the errors"
# 
# 	except (KeyboardInterrupt, SystemExit):
# 		pass
