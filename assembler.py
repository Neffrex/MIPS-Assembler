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
import os
import tempfile as temp

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

#---          ---#
#-- Exceptions --#
#---          ---#

class UndefinedMnemonic(Exception):
    mnemonic: str
    file: str
    line_number: int
    line: str

    def __init__(self, mnemonic: str, file: str, line_number: int, line: str, *args: object) -> None:
        super().__init__(*args)
        self.mnemonic = mnemonic
        self.file = file
        self.line_number = line_number
        self.line = line

    def __str__(self) -> str:
        return f"""ERROR: Undefined Mnemonic({self.mnemonic})
        \tIn file({self.file}) at line({self.line_number})
        \t\t{self.line}
        """

class InvalidSegmentContent(Exception):
    segment: str
    invalid_content: str

    def __init__(self, segment: str, invalid_content: str, *args: object) -> None:
        super().__init__(*args)
        self.segment = segment
        self.invalid_content = invalid_content

    def __str__(self) -> str:
        return f"""ERROR: Invalid Segment Content In Segment `{self.segment}`
        \tInvalid Content: {self.invalid_content}
        """
    
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

def data_callback(address:int=DATA_SEGMENT_BASE_ADDRESS):
    global location_counter
    location_counter = int(address)
    return ".data " + str(address)

def text_callback(address:int=TEXT_SEGMENT_BASE_ADDRESS):
    global location_counter
    location_counter = int(address)
    return ".text " + str(address)

def globl_callback(label):
    pass


#---                   ---#
#-- Auxiliary Functions --#
#---                   ---#

def getLimit(bytes):
    return 2 ** (bytes*8)

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

def init(argv):
    global directive_table
    global register_table
    global format_table

    directive_table = {
        ".ASCII":   ascii_callback,
        ".ASCIIZ":  asciiz_callback,
        ".BYTE":    byte_callback,
        ".HALF":    half_callback,
        ".WORD":    word_callback,
        ".TEXT":    text_callback,
        ".DATA":    data_callback,
        ".GLOBL":   globl_callback
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

    parse_ISA(argv[1])


def main():
    global symbol_table
    global opcode_table
    global ISA
    global directive_table
    global register_table
    global format_table
    global location_counter

    # Handle parameters
    if len(sys.argv) != 3:
        print("ERROR: Missing input options")
        print(f"Usage: {sys.argv[0]} <ISA_file> <source_code_file>")
        sys.exit(1)

    # Initialize tables and configurations
    init(sys.argv)
    
    # Name of the source code file
    source_name = sys.argv[2]
    # Name of the machine code file (the output file)
    output_name = os.path.splitext(source_name)[0] + ".mem"
    # Bridge file between the First and the Second Pass
    intermediate_file = temp.TemporaryFile()

    with temp.TemporaryFile(mode="w+") as intermediate_file:
        # First Pass
        with open(source_name, "r") as source_file:
            for line_number, line in enumerate(source_file):
                label, mnemonic, operands, comment = tokenize(line)

                # Handle Label
                if label:
                    # TODO: Syntax check label
                    symbol_table[label[:-1]] = location_counter
                    intermediate_file.write(f"{label} ")

                # Handle Mnemonic
                if mnemonic:
                    # Uppercase Mnemonic for case insensitive comparations
                    mnemonic_upper = mnemonic.upper()

                    if mnemonic_upper in opcode_table:
                        intermediate_file.write(f"{mnemonic} ")
                        for operand in operands:
                            intermediate_file.write(f"{operand} ")
                        intermediate_file.write("\n")
                        location_counter += INSTRUCTION_SIZE
                    elif mnemonic_upper in directive_table:
                        result = directive_table[mnemonic_upper](*operands)
                        if result != None:
                            intermediate_file.write(result + "\n")
                    else:
                        raise UndefinedMnemonic(mnemonic=mnemonic, line_number=line_number, line=line, file=source_name)
        
        # Restart intermediate file for reading
        intermediate_file.seek(0)

        # Second Pass
        with open(output_name, "w") as output_file:
            segment = None
            location_counter = 0

            for line in intermediate_file:
                label, mnemonic, operands, comment = tokenize(line)
                
                if label:
                    output_file.write(f"\n{label}\n{location_counter}/ ")
                
                if mnemonic:
                    mnemonic_upper = mnemonic.upper()

                    if mnemonic_upper.isdigit():
                        # Check valid Segment
                        if segment != ".DATA":
                            raise InvalidSegmentContent(segment=segment, invalid_content=mnemonic)
                        # Translate Data
                        for literal in [mnemonic] + operands:
                            output_file.write("{:08x} ".format(int(literal)))
                            location_counter += 1
                    elif mnemonic_upper in opcode_table:
                        # Check valid Segment
                        if segment != ".TEXT":
                            raise InvalidSegmentContent(segment=segment, invalid_content=mnemonic)
                        # Translate Instructions
                        if mnemonic_upper in ISA:
                            output_file.write(f"{parse_instruction(mnemonic, *operands)} ")
                            location_counter += 1
                    elif mnemonic_upper in directive_table:
                        segment = mnemonic_upper
                        directive_table[mnemonic_upper](*operands)

if __name__ == "__main__":
    main()
