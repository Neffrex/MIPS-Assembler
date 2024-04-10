#---
# author:  Jose Luis Pueyo Viltres
# e-mail:  joseluis.pueyo@estudiants.urv.cat
# author:  Jialiang Chen
# e-mail:  jialiang.chen@estudiants.urv.cat
# date:    Tue Apr  9 03:21:25 PM UTC 2024
# version: 0.2
#---
# A Two-Pass Assembler implementation for MIPS

import sys
import os
import tempfile as temp
# Import external modules
from modules.exceptions import *
from modules.directives import *
from modules.instructions import *

# TODO: Options to export to a configuration file
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
state = {}

#---                   ---#
#-- Auxiliary Functions --#
#---                   ---#

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
    if inst_data["FORMAT"] == "R":
        rs = parse_token(inst_data["RS"], tokens)
        rt = parse_token(inst_data["RT"], tokens)
        rd = parse_token(inst_data["RD"], tokens)
        shamt = parse_token(inst_data["SHAMT"], tokens)
        funct = parse_token(inst_data["FUNCT"], tokens)
        bin_inst = "{:06b}{:05b}{:05b}{:05b}{:05b}{:06b}".format(opcode, rs, rt, rd, shamt, funct)

    elif inst_data["FORMAT"] == "I":
        rs = parse_token(inst_data["RS"], tokens)
        rt = parse_token(inst_data["RT"], tokens)
        inm16 = parse_token(inst_data["RD"], tokens)
        bin_inst = "{:06b}{:05b}{:05b}{:016b}".format(opcode, rs, rt, inm16 % (1<<16))

    elif inst_data["FORMAT"] == "J":
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
    
    if field_symbol == "$":
        register_key = str(tokens[field_num]).replace(",", "")
        if register_key in register_table:
            return register_table[register_key]
        else:
            raise Exception(ERROR_NO_SUCH_REGISTER.format(tokens[field_num]))
    if field_symbol == "B":
        start_base = str(tokens[field_num]).find("(")+1
        end_base = str(tokens[field_num]).find(")")
        base_register = tokens[field_num][start_base:end_base]
        if base_register in register_table:
            return register_table[base_register]
        else:
            raise Exception(ERROR_NO_SUCH_REGISTER.format(base_register))
    if field_symbol == "O":
        end_offset = str(tokens[field_num]).find("(")
        offset = tokens[field_num][0:end_offset]
        if str(offset).isdigit():
            return int(offset)
        else:
            raise Exception(ERROR_WRONG_OFFSET_FORMAT.format(base_register))
    if field_symbol == "@":
        if tokens[field_num] in symbol_table:
            # Return the value of the label
            return symbol_table[tokens[field_num]]
        elif str(tokens[field_num]).isdigit():
            return int(tokens[field_num])
        else: 
            raise Exception(ERROR_WRONG_ADDRESS_FORMAT.format(tokens[field_num]))
    if field_symbol == "D":
        if tokens[field_num] in symbol_table:
            # Return the value of the label
            return symbol_table[tokens[field_num]] - (state["location_counter"]+1)
        elif str(tokens[field_num]).isdigit():
            return int(tokens[field_num]) - (state["location_counter"]+1)
        else:
            raise Exception(ERROR_WRONG_ADDRESS_FORMAT.format(tokens[field_num]))

def init(argv):
    global state
    global directive_table
    global register_table
    global format_table
    
    state = {
      "location_counter": 0
    }
    
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
    global state

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
                instruction = Instruction(line)
                label, mnemonic, operands, comment = instruction.get_tokens()

                # Handle Label
                if label:
                    # TODO: Syntax check label
                    symbol_table[label[:-1]] = state["location_counter"]
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
                        state["location_counter"] += INSTRUCTION_SIZE
                    elif mnemonic_upper in directive_table:
                        result = directive_table[mnemonic_upper](state, *operands)
                        if result != None:
                            intermediate_file.write(result + "\n")
                    else:
                        raise UndefinedMnemonic(mnemonic=mnemonic, line_number=line_number, line=line, file=source_name)
        
        # Restart intermediate file for reading
        intermediate_file.seek(0)

        # Second Pass
        with open(output_name, "w") as output_file:
            segment = None
            state["location_counter"] = 0

            for line in intermediate_file:
                instruction = Instruction(line)
                label, mnemonic, operands, comment = instruction.get_tokens()
                
                if label:
                    output_file.write(f"\n{label}\n{state['location_counter']}/ ")
                
                if mnemonic:
                    mnemonic_upper = mnemonic.upper()

                    if mnemonic_upper.isdigit():
                        # Check valid Segment
                        if segment != ".DATA":
                            raise InvalidSegmentContent(segment=segment, invalid_content=mnemonic)
                        # Translate Data
                        for literal in [mnemonic] + operands:
                            output_file.write("{:08x} ".format(int(literal)))
                            state["location_counter"] += 1
                    elif mnemonic_upper in opcode_table:
                        # Check valid Segment
                        if segment != ".TEXT":
                            raise InvalidSegmentContent(segment=segment, invalid_content=mnemonic)
                        # Translate Instructions
                        if mnemonic_upper in ISA:
                            output_file.write(f"{parse_instruction(mnemonic, *operands)} ")
                            state["location_counter"] += 1
                    elif mnemonic_upper in directive_table:
                        segment = mnemonic_upper
                        directive_table[mnemonic_upper](state, *operands)

if __name__ == "__main__":
    main()
