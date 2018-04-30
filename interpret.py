import xml.etree.ElementTree as ET
import re
import sys
import curses 
###################Classes#########################

#Class vor varibale, stores data, name and type of variable.
class variable:
	def __init__(self, *args):
		self.name = args[0]
		self.typ = 'var'
		self.value = None
		if len(args) == 2 or len(args) == 3:
			self.typ = args[1]
		if len(args) == 3:
			self.value = args[2]
			
	def __str__(self): 
		if self.value == None:
			self.value = 'None'
		string = "VARIABLE " + str(self.name)  + " with type "  + str(self.typ) + " and value " +str(self.value) 
		return string
		
#Class for storing opcode and params of instruction
class instruction_xml:
	label_position = - 1;
	
	def __init__(self, opcode, args):
		instruction_xml.label_position += 1
		self.opcode = opcode
		self.number_instructions = 0
		if len(args) == 0:
			pass
		if len(args) >= 2:
			self.arg1_type = args[0]
			self.arg1 = args[1]
			self.number_instructions = 1
		if len(args) >= 4:
			self.arg2_type = args[2]
			self.arg2 = args[3]
			self.number_instructions = 2
		if len(args) == 6:
			self.arg3_type = args[4]
			self.arg3 = args[5]
			self.number_instructions = 3
		if len(args) != 0 and len(args) != 2 and len(args) != 4 and len(args) != 6 :
			fail("Wrong ammount of arguments for instuction " + opcode + str(len(args)), 33)
		if opcode == 'LABEL':
			if self.arg1 in LABELS:
				fail("Unsuported redefintion of LABEL", 52)
			LABELS[self.arg1] = instruction_xml.label_position 
		
		
	def execute(self):
		if self.opcode == 'LABEL':
			pass
		else:
			try:
				globals()[self.opcode](self)
			except KeyError:
				fail("Undefined / unimplemented function: " + self.opcode,32)
	def __str__(self):
		string = self.opcode
		if hasattr(self, 'arg1'):
			string +=  " ARG1 " + str(self.arg1) + " ARG1_TYPE " + str(self.arg1_type)
		if hasattr(self, 'arg2'):
			string +=  " ARG2 " + str(self.arg2) + " ARG2_TYPE " + str(self.arg2_type)
		if hasattr(self, 'arg3'):
			string +=  "  ARG3: " + str(self.arg3) + " ARG3_TYPE " + str(self.arg3_type)
		return  string
#class label, forgot about it and worked with labels as asociative array. But its used somewhere. Shame on me.
class label:
	def __init__(self, name, instruction_number):
		self.name = name
		self.instruction = instruction_number
##########################METHODS###########################
#Error method
def fail(reason, exit_code):
	print(reason , file=sys.stderr)
	sys.exit(exit_code)

#Checks if var exists
def var_exists(var_name_frame):
	var_name = re.sub('^[T|G|L]F@', '', var_name_frame)
	if var_name_frame[0] == 'G':
		if var_name in GF:
			return True
	elif var_name_frame[0] == 'T':
		if TF == None:
			fail("Acces to undefined Temp FRAME.", 55)
		if var_name in TF:
			return True
	elif var_name_frame[0] == 'L':
		try:
			if var_name in LF[0]:
				return True
		except IndexError:
			fail("Acces to undefined LOCAL FRAME.", 55)
	return False
#Returns variable spcified by name
def get_var(var_name):
	if var_exists(var_name):
		if var_name[0] == 'T':
			return TF[re.sub('^TF@', '', var_name)]
		elif var_name[0] == 'G':
			return GF[re.sub('^GF@', '', var_name)]
		elif var_name[0] == 'L':
			a = LF[0][re.sub('^LF@', '', var_name)]
			return a
	else:
		fail("get_var Acces to undefined Variable:    " + var_name, 54)
		
#Fill variable with data	
def fill_var( var_name, var_type, data):
	if var_exists(var_name):
		if var_name[0] == 'T':
			global TF
			TF[re.sub('^TF@', '', var_name)].typ = var_type
			TF[re.sub('^TF@', '', var_name)].value = data
		elif var_name[0] == 'G':
			global GF
			GF[re.sub('^GF@', '', var_name)].typ = var_type
			GF[re.sub('^GF@', '', var_name)].value = data
		elif var_name[0] == 'L':
			global LF
			LF[0][re.sub('^LF@', '', var_name)].value = data
			LF[0][re.sub('^LF@', '', var_name)].typ = var_type
	else:
		fail("Acces to undefined Variable. (Fill)" + var_name, 54)

#Returns falue of variabe 
def get_value(symb_name, symb_type):
	if(symb_type == 'var'):
		ret = get_var(symb_name)
		if ret.typ == 'int':
			return int(ret.value)
		elif ret.typ == 'str' or ret.typ == 'string':
			if(ret.value == None):
				return ""
			return str(ret.value)
		elif ret.typ == 'bool':
			if ret.value == 'true':
				return True
			elif ret.value == 'false':
				return False
			else:
				fail("HOW??" + ret.value ,32)
		else:
			return ret.value
			
	elif (symb_type == 'int'):
		return int(symb_name)
	elif (symb_type == 'string'):
		return str(symb_name)
	elif (symb_type == 'bool'):
		if symb_name == 'true':
			return True
		elif symb_name == 'false':
			return False
		else:
			fail("HOW??",32)
	else:
		fail("HOW?????", 32)

#Is variable int or convertable to?
def is_int( name, typ):
	if( typ == 'var'):
		try:
			int(get_var(name).value)
			return True
		except:
			return False
	elif typ == 'int':
		return True
	return False
#Is variable bool or convertable to?
def is_bool( name, typ):
	if( typ == 'var'):
		try:
			bool(get_var(name).value)
			return True
		except:
			return False
	elif typ == 'bool':
		return True
	return False
#Is variable str or convertable to?
def is_str( name, typ):
	if( typ == 'var'):
		try:
			str(get_var(name).value)
			return True
		except:
			return False
	elif typ == 'string':
		return True
	return False	
	
#Debug instruction	
def DPRINT(instr):
	if(instr.number_instructions != 1):
		fail("Wrong ammount of arguments for DPRINT.", 32)
	print(instr.arg1 , file=sys.stderr)
#Debug instruction_number
def BREAK(instr):
	if(instr.number_instructions != 0):
		fail("Wrong ammount of arguments for BREAK.", 32)
	try:
		for var in TF:
			print("DEBUG - TF: ", TF[var], file=sys.stderr)	
		for var in TF:
			print("DEBUG - GF: ", GF[var], file=sys.stderr)	
		for var in TF:
			print("DEBUG - TL: ", TL[0][var], file=sys.stderr)
	except:
		pass
		

#Creates variable on given frame. Guess it vorks.
def MOVE(instr):
	#print("Called MOVE to", instr.arg1 ," data: ", instr.arg2 )
	if(instr.number_instructions != 2):
		fail("Wrong ammount of arguments for MOVE.", 32)
	
	#Filling with var
	if instr.arg2_type == 'var':
		fill_var( instr.arg1, get_var(instr.arg2).typ , get_var(instr.arg2).value ) 
	else:
		fill_var( instr.arg1, instr.arg2_type , instr.arg2)
		if(instr.arg2_type == 'int'):
			fill_var( instr.arg1, instr.arg2_type , re.sub('[+]', '', instr.arg2))
		
#Creates new TF, throw away the old 
def CREATEFRAME(instr):
	global TF
	TF = {}

#Pushes TF to the top of LF
def PUSHFRAME(instr):
	global TF
	if TF == None:
		fail("Acces to undefined TEMP FRAME.", 55)
	LF.insert(0,TF)
	TF = None

#Takes top of lf, puts it into TF a deletes it from LF	
def POPFRAME(instr):
	global TF
	try:
		TF = LF.pop(0)
	except:
			fail("Acces to undefined FRAME.", 55)

#Creates variable on specified frame
def DEFVAR(instr):
	if(instr.number_instructions != 1):
		fail("Wrong ammount of arguments for MOVE.", 32)
		
	var_name = re.sub('^[T|G|L]F@', '', instr.arg1)
	if instr.arg1[0] == 'T':
		if TF == None:
			fail("Acces to undefined TEMP FRAME.", 55)
		TF[var_name] = variable(var_name, instr.arg1_type)
	elif instr.arg1[0] == 'G':
		GF[var_name] = variable(var_name,instr.arg1_type)
	elif instr.arg1[0] == 'L':
		try:
			LF[0][var_name] = variable(var_name,instr.arg1_type)
		except IndexError:
			fail("Acces to undefined LOCAL FRAME.", 55)

#Value of Instruction counter +1 is saved on Data stack and changes it value depending on label
def CALL(instr):
	global INSTRUCTION_COUNTER
	if(instr.number_instructions != 1 or instr.arg1_type != 'label'):
		fail("Wrong ammount of arguments for CALL.", 32)
	CALL_STACK.append(INSTRUCTION_COUNTER+2)
	try:
		INSTRUCTION_COUNTER = LABELS[instr.arg1] - 1 
	except:
		fail("Call forbiden.",52)
#Modify Inst. counter based on CALL STACK 
def RETURN(instr):
	#print("Called Return")
	if(instr.number_instructions != 0):
		fail("Wrong ammount of arguments for RETURN.", 32)
	try:
		global INSTRUCTION_COUNTER
		try:
			INSTRUCTION_COUNTER = CALL_STACK.pop()-2
		except:
			fail("Empty stack.", 56)
	except:
		fail("U cannot jump there.", 56)
	
#Saves data to stack
def PUSHS(instr):
	if(instr.number_instructions != 1):
		fail("Wrong ammount of arguments for PUSHS.", 32)
	if(instr.arg1_type == 'var'):
		v = variable(None, instr.arg1_type, get_var(instr.arg1).value )
		DATA_STACK.append(v)
	else:
		v = variable(None, instr.arg1_type, instr.arg1 )
		DATA_STACK.append(v)
	
#Takes data from stack
def POPS(instr):
	if(instr.number_instructions != 1):
		fail("Wrong ammount of arguments for POPS.", 32)
	try:
		dest = get_var(instr.arg1)
		try:
			src = DATA_STACK.pop()
		except:
			fail("Empty stack.", 56)
		dest.value = src.value
		dest.typ = src.typ
	except:
		fail("Wrong use of POPS.", 56)
		
#Jumps to specified LABEL
def JUMP(instr):
	global INSTRUCTION_COUNTER
	if(instr.number_instructions != 1):
		fail("Wrong ammount of arguments for JUMP.", 32)
	try:
		INSTRUCTION_COUNTER =  LABELS[instr.arg1]
	except:
		fail("JUMP to unexisting LABEL.", 52)
#If arguments are of same type, AND are equal, jumps
def JUMPIFEQ(instr):
	if(instr.number_instructions != 3):
		fail("Wrong ammount of arguments for JUMP.", 32)
	
	try:
		areq = get_value(instr.arg2 , instr.arg2_type) == get_value(instr.arg3  , instr.arg3_type )
	except:
		fail("JUMPIFEQ - different data types.", 53)
	
	if areq:
		if instr.arg1 in LABELS:
			global INSTRUCTION_COUNTER
			INSTRUCTION_COUNTER = LABELS[instr.arg1]
		else:
			fail("JUMP to unexisting LABEL.", 52)

#If arguments are of same type, BUT are NOT equal, jumps
def JUMPIFNEQ(instr):
	if(instr.number_instructions != 3):
		fail("Wrong ammount of arguments for JUMP.", 32)
	
	try:
		areq = get_value(instr.arg2 , instr.arg2_type) != get_value(instr.arg3  , instr.arg3_type )
	except:
		fail("JUMPIFNEQ - different data types.", 53)
	
	if areq:
		if instr.arg1 in LABELS:
			global INSTRUCTION_COUNTER
			INSTRUCTION_COUNTER = LABELS[instr.arg1]
		else:
			fail("JUMP to unexisting LABEL.", 53)

def find_ind(match):
			return int(match.group(1)).to_bytes(1, byteorder="big")

#Output instr
def WRITE(instr):
	if(instr.number_instructions != 1):
		fail("Wrong ammount of arguments for WRITE.", 32)
	if(instr.arg1_type == 'var'):
		try:
			printed_line = get_var(instr.arg1).value.encode('utf-8')
			regex = re.compile(rb"\\(\d{1,3})")
			printed_line = regex.sub(find_ind, printed_line)
			print(printed_line.decode("ascii"))
		except:
			if(get_var(instr.arg1).value == None):
				print("")
				return
			print(get_var(instr.arg1).value)
		
	elif instr.arg1_type == 'int':
		print(int(instr.arg1))
		
	elif instr.arg1_type == 'string':
		printed_line = instr.arg1.encode('utf-8')
		regex = re.compile(rb"\\(\d{1,3})")
		printed_line = regex.sub(find_ind, printed_line)
		print(printed_line.decode("utf-8"))
		
	elif instr.arg1_type == 'bool':
		if(instr.arg1.lower() == 'true'):
			print('true')
		else:
			print('false')
		
def READ(instr):
	if(instr.number_instructions != 2):
		fail("Wrong ammount of arguments for READ.", 32)
	try:
		st = input()
	except:
		st =''
	if instr.arg2 == 'int':
		try:
			fill_var( instr.arg1, 'int', int(st))
		except:
			fill_var( instr.arg1, 'int', 0)
	if instr.arg2 == 'string':
		try:
			fill_var( instr.arg1, 'string', str(st))
		except:
			fill_var( instr.arg1, 'string', '')
	if instr.arg2 == 'bool':
		try:
			st = st.upper()
			if st == 'TRUE':
				fill_var( instr.arg1, 'bool', 'true')
			else:
				fill_var( instr.arg1, 'bool', 'false')	
		except:
			fill_var( instr.arg1, 'bool', 'false')
	
#ARITMETIC
def ADD(instr):
	if(instr.number_instructions != 3):
		fail("Wrong ammount of arguments for ADD.", 32)
	if is_int(instr.arg2, instr.arg2_type) and is_int(instr.arg3, instr.arg3_type):
		filling = int(get_value(instr.arg2, instr.arg2_type)) + int(get_value(instr.arg3, instr.arg3_type))
		fill_var( instr.arg1, 'int', filling)
	else:
		fail("Not INTS for ADD.", 53)
		
def SUB(instr):
	if(instr.number_instructions != 3):
		fail("Wrong ammount of arguments for SUB.", 32)
	if is_int(instr.arg2, instr.arg2_type) and is_int(instr.arg3, instr.arg3_type):
		filling = int(get_value(instr.arg2, instr.arg2_type)) - int(get_value(instr.arg3, instr.arg3_type))
		fill_var( instr.arg1, 'int', filling)
	else:
		fail("Not INTS for SUB.", 53)

def MUL(instr):#TODO TEST
	if(instr.number_instructions != 3):
		fail("Wrong ammount of arguments for MUL.", 32)
	if is_int(instr.arg2, instr.arg2_type) and is_int(instr.arg3, instr.arg3_type):
		filling = int(get_value(instr.arg2, instr.arg2_type)) * int(get_value(instr.arg3, instr.arg3_type))
		fill_var( instr.arg1, 'int', filling)
	else:
		fail("Not INTS for MUL.", 53)

def IDIV(instr):
	if(instr.number_instructions != 3):
		fail("Wrong ammount of arguments for IDIV.", 32)
	if is_int(instr.arg2, instr.arg2_type) and is_int(instr.arg3, instr.arg3_type):
		if ( int(get_value(instr.arg3, instr.arg3_type)) == 0 ):
			fail("Division by zero",57)
		filling = int(get_value(instr.arg2, instr.arg2_type)) // int(get_value(instr.arg3, instr.arg3_type))
		fill_var( instr.arg1, 'int', filling)
	else:
		fail("Not INTS for IDIV.", 53)
				
#Comparison - Lesser Than
def LT(instr):
	if(instr.number_instructions != 3):
		fail("Wrong ammount of arguments for LT.", 32)
	try:
		areq = get_value(instr.arg2 , instr.arg2_type) < get_value(instr.arg3  , instr.arg3_type )
	except:
		fail("JUMPIFEQ - different data types.", 53)
	
	if areq:
		fill_var( instr.arg1, 'bool', 'true')
	else:
		fill_var( instr.arg1, 'bool', 'false')
		
#Comparison - Greater Than
def GT(instr):
	if(instr.number_instructions != 3):
		fail("Wrong ammount of arguments for GT.", 32)
	try:
		areq = get_value(instr.arg2 , instr.arg2_type) > get_value(instr.arg3  , instr.arg3_type )
	except:
		fail("JUMPIFEQ - different data types.", 53)
	
	if areq:
		fill_var( instr.arg1, 'bool', 'true')
	else:
		fill_var( instr.arg1, 'bool', 'false')
		
#Comparison - equal
def EQ(instr):
	if(instr.number_instructions != 3):
		fail("Wrong ammount of arguments for EQ.", 32)
	
	try:
		areq = get_value(instr.arg2 , instr.arg2_type) == get_value(instr.arg3  , instr.arg3_type )
	except:
		fail("EQ - different data types.", 53)
	
	if areq:
		fill_var( instr.arg1, 'bool', 'true')
	else:
		fill_var( instr.arg1, 'bool', 'false')
		
def AND(instr):
	if(instr.number_instructions != 3):
		fail("Wrong ammount of arguments for AND.", 32)
	if is_bool(instr.arg2, instr.arg2_type) and is_bool(instr.arg3, instr.arg3_type):
		filling = bool(get_value(instr.arg2, instr.arg2_type)) and bool(get_value(instr.arg3, instr.arg3_type))
		if filling == True:
			filling = 'true'
		else:
			filling = 'false'
		fill_var( instr.arg1, 'bool', filling)
	else:
		fail("Not BOOLS for ADD.", 53)
		
def OR(instr):
	if(instr.number_instructions != 3):
		fail("Wrong ammount of arguments for OR.", 32)
	if is_bool(instr.arg2, instr.arg2_type) and is_bool(instr.arg3, instr.arg3_type):
		filling = bool(get_value(instr.arg2, instr.arg2_type)) or bool(get_value(instr.arg3, instr.arg3_type))
		if filling == True:
			filling = 'true'
		else:
			filling = 'false'
		fill_var( instr.arg1, 'bool', filling)
	else:
		fail("Not BOOLS for ADD.", 53)
		
def NOT(instr):
	if(instr.number_instructions != 2):
		fail("Wrong ammount of arguments for NOT.", 32)
	if is_bool(instr.arg2, instr.arg2_type):
		filling = not bool(get_value(instr.arg2, instr.arg2_type))
		if filling == True:
			filling = 'true'
		else:
			filling = 'false'
		fill_var( instr.arg1, 'bool', filling)
	else:
		fail("Not BOOLS for NOT.", 53)

def INT2CHAR(instr):
	if(instr.number_instructions != 2):
		fail("Wrong ammount of arguments for NOT.", 32)
	try:
		fill_var( instr.arg1, 'str', chr(get_value(instr.arg2, instr.arg2_type)))
	except:
		fail("INT2CHAR",58)
		
def STRI2INT(instr):
	if(instr.number_instructions != 3):
		fail("Wrong ammount of arguments for NOT.", 32)
	try:
		if instr.arg3_type == 'var':
			index = get_var(instr.arg3).value
		else:
			index = int(instr.arg3)
		if instr.arg2_type == 'var':
			
			num = get_value(instr.arg2, 'var')
			fill_var( instr.arg1, 'var', ord(num[index]))
		elif instr.arg2_type == 'string':
			fill_var( instr.arg1, 'var', ord(instr.arg2[index]))
		else:
			fail("STRI2INT Not string nor anything accetable",53)
	except:
		fail("STRI2INT",58)
		
def CONCAT(instr):
	if(instr.number_instructions != 3):
		fail("Wrong ammount of arguments for CONCAT.", 32)
	if is_str(instr.arg2, instr.arg2_type) and is_str(instr.arg3, instr.arg3_type):
		filling = ""
		if(get_value(instr.arg2, instr.arg2_type) != 'None'):
			filling += str(get_value(instr.arg2, instr.arg2_type)) 
		if(get_value(instr.arg3, instr.arg3_type) != 'None'):
			filling += str(get_value(instr.arg3, instr.arg3_type))
		fill_var( instr.arg1, 'string', filling)
	else:
		fail("Not STRINGS for CONCAT.", 53)

def GETCHAR(instr):
	if(instr.number_instructions != 3):
		fail("Wrong ammount of arguments for GETCHAR.", 32)
	if is_str(instr.arg2, instr.arg2_type) and is_int(instr.arg3, instr.arg3_type):
		try:
			if var_exists(instr.arg2):
				printed_line = get_var(instr.arg2).value.encode('ascii')
			else:
				printed_line = instr.arg2.encode('ascii')
			regex = re.compile(rb"\\(\d{1,3})")
			printed_line = regex.sub(find_ind, printed_line)
			printed_line = printed_line.decode("utf-8")
			filling = str(printed_line)[int(get_value(instr.arg3, instr.arg3_type))]
		except IndexError:
			fail("GETCHAR", 58)
		fill_var( instr.arg1, 'string', filling)
	else:
		fail("Not STRINGS for GETCHAR.", 53)

def SETCHAR(instr):
	if(instr.number_instructions != 3):
		fail("Wrong ammount of arguments for SETCHAR.", 32)
	if is_int(instr.arg2, instr.arg2_type) and is_str(instr.arg3, instr.arg3_type):
		try:
			if var_exists(instr.arg3):
				sub = str(get_value(instr.arg3, instr.arg3_type))[0]
			else:
				sub = str(instr.arg3)[0]
			
			filling = str(get_value(instr.arg1, instr.arg1_type))
			
			filling = list(filling)
			filling[int(get_value(instr.arg2, instr.arg2_type))]=sub
			filling = "".join(filling)
			fill_var( instr.arg1, 'string', filling)
		except:
			fail("SETCHAR", 53)
	else:
		fail("Not STRINGS for CONCAT.", 53)
		
def STRLEN(instr):
	if(instr.number_instructions != 2):
		fail("Wrong ammount of arguments for STRLEN.", 32)
	if is_str(instr.arg2, instr.arg2_type):
	
		if instr.arg2_type == 'var':
			printed_line = get_var(instr.arg2).value
		else:
			printed_line = instr.arg2
		if(printed_line == None):
			fill_var( instr.arg1, 'int', 0)
			return
		printed_line = printed_line.encode('utf-8')
		regex = re.compile(rb"\\(\d{1,3})")
		printed_line = regex.sub(find_ind, printed_line)
		try:
			fill_var( instr.arg1, 'int', len(printed_line.decode("utf-8")))
		except:
			fill_var( instr.arg1, 'int', len(printed_line))
	else:
		fail("Not STRINGS for STRLEN.", 53)
		
def TYPE(instr):
	if(instr.number_instructions != 2):
		fail("Wrong ammount of arguments for TYPE.", 32)

	if instr.arg2_type == 'var':	
		var_type = get_var(instr.arg2).typ
		if var_type == 'string':
			fill_var( instr.arg1, 'str', 'string')
		elif var_type == 'bool':
			fill_var( instr.arg1, 'str', 'bool')
		elif var_type == 'int':
			fill_var( instr.arg1, 'str', 'int')
		else:
			fill_var( instr.arg1, 'str', '')
	else:
			fill_var( instr.arg1, 'str', instr.arg2_type)

#Main
#ARG parse
if len(sys.argv) != 2:
	print("See --help")
	sys.exit(1)

if sys.argv[1] == '--help':
	print("Help")
	sys.exit(0)
elif re.match('^--source=.*', sys.argv[1]):
	filename = re.sub('^--source=', '', sys.argv[1])
else:
	print("See --help")
	sys.exit(0)
	
TF = None
GF = {}
LF = [{}]
DATA_STACK = []
CALL_STACK = []
instructions = []
arguments = []
LABELS={} 

	
try:
	tree = ET.parse(filename)
	root = tree.getroot()
except:
	fail("Chybne vtupni XML", 31)
	
#Load all instructions to an array of instructions 
for instr in root:
	for arg in instr:
		arguments.append(arg.attrib['type'])
		arguments.append(arg.text)
	instructions.append(instruction_xml(instr.attrib['opcode'], arguments))
	arguments = []

#Let evry intruction execute itself
INSTRUCTION_COUNTER = 0	
while INSTRUCTION_COUNTER < len(root):
	#print("  Executing ",instructions[INSTRUCTION_COUNTER]);
	instructions[INSTRUCTION_COUNTER].execute()
	INSTRUCTION_COUNTER += 1
	
