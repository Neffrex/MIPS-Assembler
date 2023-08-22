#!/usr/bin/env python3
#---
# author:  Jose Luis Pueyo Viltres
# e-mail:  joseluis.pueyo@estudiants.urv.cat
# author:  Jialiang Chen
# date:    jialiang.chen@estudiants.urv.cat
# version: 0.1
#---
# A Two-Pass [Macro] Assembler implementation for MIPS

# Data Structures

#OpCodeTable = #Mnemonic #OpCode #Type #Length?(Only in Dynamic Length Instructions)
#e.g           ADD       0x0     RR    

#SymbolTable = #Label #LocationCounter
               #main: 0
               #pow:  5

archivo = """
########################################################
# Implementation using MIPS assembly
# C interface:
#            int Mult (int a,int b)
########################################################

# Mult: multiplica a por b y guarda el resultado en s
# Preconditions:   
#   1st parameter (a0) a
#   2nd parameter (a1) b
# Postconditions:
#   s = a * b
#Utiliza las instrucciones: lw, sw, and, or, add, sub, slt, beq y j

.text
.globl main

#main: inicio del programa
#   registros: 	
#   $zero -&gt; 0d = 0h
#	    $t1 -&gt; 9d = 9h
#		$a0 -&gt; 4d = 4h
#		$a1 -&gt; 5d = 5h
#		$s0 -&gt; 16d = 10h
#		$s1 -&gt; 17d = 11h

main:   
   lw   $t1, 100($zero)    # carga la constante "1"
   lw   $a0, 101($zero)    # carga el valor de a
   lw   $a1, 102($zero)    # carga el valor de b

   

   or   $s2, $a1, $zero    # j := b
   or   $s3, $t1, $zero    # k := 1
pow:
   
   slt  $t0, $s2, $t1      # j < 1?
   beq  $t0, $t1, fipow    # si (j < 1) entonces (pc = fipow)
   and  $s1, $zero, $zero  # i := 0
   and  $s0, $zero, $zero  # s := 0

   per:

	# si (i >= a) entonces (pc = fiper)
      slt  $t0, $s1, $a0       # i < a ?
      beq  $t0, $zero, fiper   # si NOT(i < a) entonces (pc = fiper)

      add  $s0, $s0, $s3       # s := s + k
      add  $s1, $s1, $t1       # i := i + 1

      j per

   fiper:

   or $s3, $s0, $zero   # k := s

   sub  $s2, $s2, $t1   # j := j - 1
   j pow

fipow:

   sw $s0, 103($zero)    # salva s

fi:
   j fi # bucle infinito


.data 

uno: .asciiz "1"
a: .asciiz "3"
b: .asciiz "5"
s: .asciiz "x"

"""

# TODO: Options to export to a configuration file
DATA_SEGMENT_BASE_ADDRESS = 0x64
TEXT_SEGMENT_BASE_ADDRESS = 0
COMMENT_SYMBOL = "#"

# Constant Values
WORD_SIZE = 4 #Bytes
HALF_SIZE = 2 #Bytes
BYTE_SIZE = 1 #Bytes
CHAR_SIZE = 1 #Bytes
INSTRUCTION_SIZE = WORD_SIZE

# Functions

def getLimit(bytes):
    return 2 ** (bytes*8)

def ascii_callback(*literals):
    global location_counter
    result = ""
    for literal in literals:
        for char in literal[1:-1]:
            result += str.format("{:02x}", ord(char))
            location_counter += CHAR_SIZE
    return result

def asciiz_callback(*literals):
    global location_counter
    result = ""
    for literal in literals:
        result += ascii_callback(literal)+'\0'
        # The location_counter is incremented inside the ascii_callback() function
        # Therefore, it only needs to count the additional '\0'
        location_counter += CHAR_SIZE
    return result

def byte_callback(*literals):
    global location_counter
    result = ""
    for literal in literals:
        if (abs(int(literal)) > getLimit(BYTE_SIZE)):
            raise Exception(f"Operand {literal} exceeds the size of a byte ({getLimit(BYTE_SIZE)})")
        result += str.format("{:02x}", int(literal))
        location_counter += BYTE_SIZE
    return result

def half_callback(*literals):
    global location_counter
    result = ""
    for literal in literals:
        if (abs(int(literal)) > getLimit(HALF_SIZE)):
            raise Exception(f"Operand {literal} exceeds the size of a half ({getLimit(HALF_SIZE)})")
        result += str.format("{:04x}", int(literal))
        location_counter += HALF_SIZE
    return result

def word_callback(*literals):
    # TODO
    global location_counter
    result = ""
    for literal in literals:
        if (abs(int(literal)) > getLimit(WORD_SIZE)):
            raise Exception(f"Operand {literal} exceeds the size of a word ({getLimit(WORD_SIZE)})")
        result += str.format("{:08x}", int(literal))
        location_counter += WORD_SIZE
    return result

def data_callback(address=DATA_SEGMENT_BASE_ADDRESS):
    global location_counter
    location_counter = address

def text_callback(address=TEXT_SEGMENT_BASE_ADDRESS):
    global location_counter
    location_counter = address

def globl_callback(label):
    pass

# Variables
symbol_table = dict()
opcode_table = {
    "ADD": (0x20, 'R'),
    "SUB": (0x22, 'R'),
    "AND": (0x24, 'R'),
    "OR" : (0x25, 'R'),
    "SLT": (0x2A, 'R'),
    "LW" : (0x23, 'I'),
    "SW" : (0x2B, 'I'),
    "BEQ": (0x4 , 'I'),
    "J"  : (0x2 , 'J')
}
directive_table = {
    ".ascii": ascii_callback,
    ".asciiz": asciiz_callback,
    ".byte": byte_callback,
    ".half": half_callback,
    ".word": word_callback,
    ".text": text_callback,
    ".data": data_callback,
    ".globl": globl_callback
}
location_counter = -1

# Splits the line in 4 fields: Label, Mnemonic, Operands and Comment
# Label: String, Mnemonic: String, Operands: List(String), Comment: String
# In case of a field that is not present in the line it would asign `None` to it
def tokenize(line):
    label = mnemonic = comment = None
    operands = []
    
    # Identify Comment
    tokens = line.split(COMMENT_SYMBOL, 1)
    comment = tokens[1] if len(tokens) > 1 else None

    # Handle the Functional Tokens
    phase = 0
    uncommented_tokens = tokens[0].replace(',',' ').split()
    while len(uncommented_tokens) > 0:
        match phase:
            case 0: # Possible Label
                if uncommented_tokens[0].endswith(":"):
                    label = uncommented_tokens[0]
                    del uncommented_tokens[0]
            case 1: # Mnemonic
                mnemonic = uncommented_tokens[0]
            case 2: # Operands
                operands = uncommented_tokens[1:]
                break
        phase+=1
    
    return label, mnemonic, operands, comment


for line_number, line in enumerate(archivo.split("\n")):
    
    # Tokenize the line
    label, mnemonic, operands, comment = tokenize(line)

    # Handle Label
    if label:
        symbol_table[label] = location_counter

    # Handle Mnemonic (Instruction / Directive)
    if mnemonic:
        mnemonic_upper=str.upper(mnemonic)
        if mnemonic_upper in opcode_table:
            # TODO Write in intermediate file
            print(mnemonic, operands)
            location_counter += INSTRUCTION_SIZE
        elif mnemonic in directive_table:
            # Callback function with optional operands
            result = directive_table[mnemonic](*operands)
            if result != None:
                print(result)
        else:
            raise Exception(f"Undefined Mnemonic: {mnemonic}")
