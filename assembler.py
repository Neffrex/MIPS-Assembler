#!/usr/bin/env python3
#---
# author:  Jose Luis Pueyo Viltres
# e-mail:  joseluis.pueyo@estudiants.urv.cat
# author:  Jialiang Chen
# date:    jialiang.chen@estudiants.urv.cat
# version: 0.1
#---
# A Two-Pass Assembler implementation for MIPS

import sys

# TODO: Options to export to a configuration file
DATA_SEGMENT_BASE_ADDRESS = 0x64
TEXT_SEGMENT_BASE_ADDRESS = 0x0
COMMENT_SYMBOL = "#"

# Constant Values
CHAR_SIZE = 1
BYTE_SIZE = 1
HALF_SIZE = 1
WORD_SIZE = 1
INSTRUCTION_SIZE = WORD_SIZE

#---         ---#
#-- Variables --#
#---         ---#

symbol_table = {}
# TODO: Export opcode table as a modifiable file
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
ISA = {}
directive_table = {}
register_table = {}
format_table = {}
location_counter = -1

#---                            ---#
#-- Directive callback functions --#
#---                            ---#

def ascii_callback(*literals):
    global location_counter
    result = ""
    for literal in literals:
        for char in literal[1:-1]:
            #result += str.format("{:02x}", ord(char))
            result += f"{ord(char)} "
            location_counter = int(location_counter) + CHAR_SIZE
    return result

def asciiz_callback(*literals):
    global location_counter
    result = ""
    for literal in literals:
        #result += ascii_callback(literal) + str(0)
        result += f"{ascii_callback(literal)} 0 "
        # The location_counter is incremented inside the ascii_callback() function
        # Therefore, it only needs to count the additional '\0'
        location_counter = int(location_counter) + CHAR_SIZE
    return result

def byte_callback(*literals):
    global location_counter
    result = ""
    for literal in literals:
        if (abs(int(literal)) > getLimit(BYTE_SIZE)):
            raise Exception(f"Operand {literal} exceeds the size of a byte ({getLimit(BYTE_SIZE)})")
        #result += str.format("{:02x}", int(literal))
        result += f"{literal} "
        location_counter = int(location_counter) + BYTE_SIZE
    return result

def half_callback(*literals):
    global location_counter
    result = ""
    for literal in literals:
        if (abs(int(literal)) > getLimit(HALF_SIZE)):
            raise Exception(f"Operand {literal} exceeds the size of a half ({getLimit(HALF_SIZE)})")
        #result += str.format("{:04x}", int(literal))
        result += f"{literal} "
        location_counter = int(location_counter) + HALF_SIZE
    return result

def word_callback(*literals):
    global location_counter
    result = ""
    for literal in literals:
        if (abs(int(literal)) > getLimit(WORD_SIZE)):
            raise Exception(f"Operand {literal} exceeds the size of a word ({getLimit(WORD_SIZE)})")
        #result += str.format("{:08x}", int(literal))
        result += f"{literal} "
        location_counter = int(location_counter) + WORD_SIZE
    return result

def data_callback(address=DATA_SEGMENT_BASE_ADDRESS):
    global location_counter
    location_counter = int(address)
    return ".data " + str(address)

def text_callback(address=TEXT_SEGMENT_BASE_ADDRESS):
    global location_counter
    location_counter = int(address)
    return ".text " + str(address)

def globl_callback(label):
    #return ".globl " + str(label)
    pass

def end_callback():
    return ".end"

#---                   ---#
#-- Auxiliary Functions --#
#---                   ---#

def getLimit(bytes):
    return 2 ** (bytes*8)

def effective_address(base, offset):
  pass

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
                    label = uncommented_tokens[0][0:-1]
                    del uncommented_tokens[0]
            case 1: # Mnemonic
                mnemonic = uncommented_tokens[0]
            case 2: # Operands
                operands = uncommented_tokens[1:]
                break
        phase+=1
    
    return label, mnemonic, operands, comment

def parse_ISA(file_path):
    global ISA  # Dictionary to store the parsed data

    with open(file_path, 'r') as file:
        columns = ["OP", "RS", "RT", "RD", "SHAMT", "FUNCT", "FORMAT", "COMMENT"]
        
        for line in file:
            line = line.strip()  # Remove leading/trailing whitespace
            
            # Skip empty lines and lines starting with '#'
            if not line or line.startswith('#'):
                continue
            
            row_data = line.split()  # Split the line into columns
            instruction = row_data[0]  # The instruction name
            
            ISA[instruction] = {}  # Create an inner dictionary for the instruction
            
            # Fill the inner dictionary with the column values
            for i, column_value in enumerate(row_data[1:]):
                column_name = columns[i]
                ISA[instruction][column_name] = column_value
    return ISA

def parse_instruction(*tokens):
    global ISA

    op = str(tokens[0]).upper()
    inst_data = ISA[op]
    opcode = int(inst_data["OP"], 2)
    # TODO: Check if every field of the `inst_data` is valid, and consider changing the parser so the `-` don't define any entry on the ISA
    match inst_data["FORMAT"]:
        case "R":
            rs = parse_token(inst_data["RS"], tokens)
            rt = parse_token(inst_data["RT"], tokens)
            rd = parse_token(inst_data["RD"], tokens)
            shamt = parse_token(inst_data["SHAMT"], tokens)
            funct = parse_token(inst_data["FUNCT"], tokens)
            bin_inst = "{:06b}{:05b}{:05b}{:05b}{:05b}{:06b}".format(opcode, rs, rt, rd, shamt, funct)
        case "I":
            rs = parse_token(inst_data["RS"], tokens)
            rt = parse_token(inst_data["RT"], tokens)
            inm16 = parse_token(inst_data["RD"], tokens)
            bin_inst = "{:06b}{:05b}{:05b}{:016b}".format(opcode, rs, rt, inm16 % (1<<16))
        case "J":
            Inm26 = parse_token(inst_data["RS"], tokens)
            bin_inst = "{:06b}{:026b}".format(opcode, Inm26)
    return("{:08X}".format(int(bin_inst, 2)))



def parse_token(format, tokens):
    field_symbol = format[0]
    field_num = int(format[1])

    ERROR_NO_SUCH_REGISTER = "ERROR: No such register called `{}`."
    ERROR_WRONG_OFFSET_FORMAT = "ERROR: The Offset `{}` is not a digit."
    ERROR_WRONG_ADDRESS_FORMAT = "ERROR: The Address `{}` is not a label nor a number."

    if str(format).isdigit():
        return int(format, 2)
    
    match field_symbol:
        case "$":
            
            register_key = str(tokens[field_num]).replace(",", "")
            if register_key in register_table:
                return register_table[register_key]
            else:
                raise Exception(ERROR_NO_SUCH_REGISTER.format(tokens[field_num]))
        case "B":
            start_base = str(tokens[field_num]).find("(")+1
            end_base = str(tokens[field_num]).find(")")
            base_register = tokens[field_num][start_base:end_base]
            if base_register in register_table:
                return register_table[base_register]
            else:
                raise Exception(ERROR_NO_SUCH_REGISTER.format(base_register))
        case "O":
            end_offset = str(tokens[field_num]).find("(")
            offset = tokens[field_num][0:end_offset]
            if str(offset).isdigit():
                return int(offset)
            else:
                raise Exception(ERROR_WRONG_OFFSET_FORMAT.format(base_register))
        case "@":
            if tokens[field_num] in symbol_table:
                # Return the value of the label
                return symbol_table[tokens[field_num]]
            elif str(tokens[field_num]).isdigit():
                return int(tokens[field_num])
            else: 
                raise Exception(ERROR_WRONG_ADDRESS_FORMAT.format(tokens[field_num]))
        case "D":
            if tokens[field_num] in symbol_table:
                # Return the value of the label
                return symbol_table[tokens[field_num]] - (location_counter+1)
            elif str(tokens[field_num]).isdigit():
                return int(tokens[field_num]) - (location_counter+1)
            else:
                raise Exception(ERROR_WRONG_ADDRESS_FORMAT.format(tokens[field_num]))

def init():
    global directive_table
    global register_table
    global format_table

    directive_table = {
        ".ascii":   ascii_callback,
        ".asciiz":  asciiz_callback,
        ".byte":    byte_callback,
        ".half":    half_callback,
        ".word":    word_callback,
        ".text":    text_callback,
        ".data":    data_callback,
        ".globl":   globl_callback,
        ".end":     end_callback
    }

    # TODO: Considerate change this table to an enum
    register_table = {
        "$zero":0,
        "$at":  1,
        "$v0":  2,
        "$v1":  3,
        "$a0":  4,
        "$a1":  5,
        "$a2":  6,
        "$a3":  7,
        "$t0":  8,
        "$t1":  9,
        "$t2":  10,
        "$t3":  11,
        "$t4":  12,
        "$t5":  13,
        "$t6":  14,
        "$t7":  15,
        "$s0":  16,
        "$s1":  17,
        "$s2":  18,
        "$s3":  19,
        "$s4":  20,
        "$s5":  21,
        "$s6":  22,
        "$s7":  23,
        "$t8":  24,
        "$t9":  25,
        "$k0":  26,
        "$k1":  27,
        "$gp":  28,
        "$sp":  29,
        "$fp":  30,
        "$ra":  31,

    }

    format_table = {
        "R": "{:06b}{:05b}{:05b}{:05b}{:05b}{:06b}",
        "I": "{:06b}{:05b}{:05b}{:016b}",
        "J": "{:06b}{:026b}"
    }

    parse_ISA("/home/casa/Documents/Python/MIPS-Assembler/ISA.cfg")


def main():
    global symbol_table
    global opcode_table
    global ISA
    global directive_table
    global register_table
    global format_table
    global location_counter

    # Initialize tables and configurations
    init()

    # TODO: Asign the first parameter to the source code name
    # Name of the source code file
    source_code_name = "/home/casa/Documents/Python/MIPS-Assembler/mult.asm"
    # Name of the halfway code file
    halfway_code_name = source_code_name + '.tmp'
    # Name of the machine code file, the output file
    machine_code_name = str(source_code_name).split(".")[0] + '.mem'
    
    # Open the files
    source_code = open(source_code_name, 'r')
    source_lines = source_code.readlines()
    halfway_code = open(halfway_code_name, 'w')

    # First Pass of the assembler
    for line in source_lines:
        # Tokenize the line
        label, mnemonic, operands, comment = tokenize(line)

        # Handle Label
        if label:
            symbol_table[label] = location_counter
            halfway_code.write(label + ":\n")

        # Handle Mnemonic (Instruction / Directive)
        if mnemonic:
            mnemonic_upper=str.upper(mnemonic)
            if mnemonic_upper in opcode_table:
                halfway_code.write(mnemonic + " " + " ".join(str(operand) for operand in operands))
                halfway_code.write("\n")
                location_counter += INSTRUCTION_SIZE
            elif mnemonic in directive_table:
                # Callback function with optional operands
                result = directive_table[mnemonic](*operands)
                if result != None:
                    halfway_code.write(result + "\n")
            else:
                raise Exception(f"Undefined Mnemonic: {mnemonic}")
    halfway_code.write(".end\n")

    # Handle files
    halfway_code.close()
    halfway_code = open(halfway_code_name, 'r')
    machine_code = open(machine_code_name, 'w')

    segment = None
    halfway_lines = halfway_code.readlines()
    # Second Pass of the assembler
    location_counter = 0
    for line in halfway_lines:
        tokens = line.split()
        # Handle Segment Directive
        if tokens[0] == ".text" or tokens [0] == ".data":
            segment = tokens[0]
            location_counter = int(tokens[1])
            continue

        if tokens[0] == ".end":
            machine_code.write("\n")
            break
    
        if tokens[0].endswith(":"):
            machine_code.write("\n# {}\n {:02X}/ ".format(tokens[0], location_counter))
            continue

        # Handle Instructions/Data
        if segment == ".text":
            # Text segment
            mnemonic = tokens[0]
            mnemonic_upper = mnemonic.upper()
            if (mnemonic_upper in ISA):
                machine_code.write(f"{parse_instruction(*tokens)} ")
                location_counter += int(INSTRUCTION_SIZE)
            else:
                raise Exception(f"ERROR: No such instruction: {mnemonic}")
        elif segment == ".data":
            # Data segment
            for token in tokens:
                machine_code.write("{:08X} ".format(int(token)))
                location_counter += int(WORD_SIZE)
        else:
            # Undefined segment
            raise Exception("Error: No segment specified, try adding the directives `.text` or `.data` before the start of a segment")

    halfway_code.close()

if __name__ == "__main__":
    main()