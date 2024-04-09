#---                            ---#
#-- Directive callback functions --#
#---                            ---#

CHAR_SIZE = 1
BYTE_SIZE = 1
HALF_SIZE = 1
WORD_SIZE = 1

DATA_SEGMENT_BASE_ADDRESS = 0x64
TEXT_SEGMENT_BASE_ADDRESS = 0x00

def get_limit(bytes):
  return 2 ** (bytes*8)

def ascii_callback(state, *literals):
    result = ""
    for literal in literals:
        for char in literal[1:-1]:
            #result += str.format("{:02x}", ord(char))
            result += f"{ord(char)} "
            state["location_counter"] = int(state["location_counter"]) + CHAR_SIZE
    return result

def asciiz_callback(state, *literals):
    result = ""
    for literal in literals:
        #result += ascii_callback(literal) + str(0)
        result += f"{ascii_callback(literal)} 0 "
        # The state["location_counter"] is incremented inside the ascii_callback() function
        # Therefore, it only needs to count the additional '\0'
        state["location_counter"] = int(state["location_counter"]) + CHAR_SIZE
    return result

def byte_callback(state, *literals):
    result = ""
    for literal in literals:
        if (abs(int(literal)) > get_limit(BYTE_SIZE)):
            raise Exception(f"Operand {literal} exceeds the size of a byte ({get_limit(BYTE_SIZE)})")
        #result += str.format("{:02x}", int(literal))
        result += f"{literal} "
        state["location_counter"] = int(state["location_counter"]) + BYTE_SIZE
    return result

def half_callback(state, *literals):
    result = ""
    for literal in literals:
        if (abs(int(literal)) > get_limit(HALF_SIZE)):
            raise Exception(f"Operand {literal} exceeds the size of a half ({get_limit(HALF_SIZE)})")
        #result += str.format("{:04x}", int(literal))
        result += f"{literal} "
        state["location_counter"] = int(state["location_counter"]) + HALF_SIZE
    return result

def word_callback(state, *literals):
    result = ""
    for literal in literals:
        if (abs(int(literal)) > get_limit(WORD_SIZE)):
            raise Exception(f"Operand {literal} exceeds the size of a word ({get_limit(WORD_SIZE)})")
        #result += str.format("{:08x}", int(literal))
        result += f"{literal} "
        state["location_counter"] = int(state["location_counter"]) + WORD_SIZE
    return result

def data_callback(state, address:int=DATA_SEGMENT_BASE_ADDRESS):
    state["location_counter"] = int(address)
    return ".data " + str(address)

def text_callback(state, address:int=TEXT_SEGMENT_BASE_ADDRESS):
    state["location_counter"] = int(address)
    return ".text " + str(address)

def globl_callback(state, label):
    pass

