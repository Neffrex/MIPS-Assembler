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
#opcode = {
#    "lw": 0x23,
#    "sw": 0x2B,
#    "beq": 0x4,
#    "j": 0x2,
#}
#funct = {
#    "add": 0x20,
#    "sub": 0x22,
#    "and": 0x24,
#    "or": 0x25,
#    "slt": 0x2A,
#}
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
    ".ascii",
    ".asciiz",
    ".byte",
    ".half",
    ".word",
    ".text",
    ".data",
    ".globl"
}
location_counter = 0


# Transforms the line into a set of tokens
def tokenize (line):
    replacements = {
        "\t": " ",
        "(" : " ",
        ")" : "",
        "," : "",
    }
    # Translates some characters following the table above
    transformation = line.translate(str.maketrans(replacements))
    # Remove comments
    transformation = transformation.split("#", 1)[0]
    # Filter empty token
    transformation = filter(None, transformation.split(" "))
    # Return the transformation ass a list
    return list(transformation)

# Checks if the token is a label and appends it to the symbol table if it is
def check_label (token):
    # Check if there's a label
    if token[-1] == ':':
        if token in symbol_table:
            # throw error
            pass
        
        # It is a label
        return True
    # It is NOT a label
    return False

def process_directive(directive):
    print(directive)


for line_number, line in enumerate(archivo.split("\n")):
    
    # Tokenize the line
    tokens = tokenize(line)

    # Ignore in case of a comment or a blank line
    if len(tokens) == 0 or tokens[0][0:1] == '#':
        continue
    
    current_token = tokens[0]

    # Check for label
    if check_label(current_token):
        # Append the label to the symbol table
        symbol_table[current_token[0:-1]] = location_counter
        del(tokens[0])

    if len(tokens) != 0:
        current_token = tokens[0]
    else:
        continue

    if str.upper(current_token) in opcode_table:
        # Is an instruction
        print(str.upper(current_token))
        # TODO: Process tokens
        location_counter += 1
    elif current_token in directive_table:
        # Is a directive
        process_directive(tokens[tokens.index(current_token):len(tokens)])
    else:
        raise Exception("Wrong Mnemonic %(current_token)s")

    
#print(symbol_table)