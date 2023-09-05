# What is this proyect?

This is a Two-Pass Assembler for MIPS implemented with Python.

**It is design as an auxiliary programm for a custom implementation of a CPU**

Keep in mind that it doesn't have all the functionality you would expect from a MIPS Assembler.

# :warning: (**WIP**) Customizable options

* Output format (e.g Keep labels in comments)
* Split *data* and *text* segments in different files 
* Define the segments dynamically or statically

# :memo: Valid directives

| Syntax              | Description                                                                                 |
| ------------------- | --------------------------------------------------------------------------------------------|
| .ascii *str*        | Saves the String (str) in memory                                                            |
| .asciiz *str*       | Saves the String (str), appending a final *null* value, in memory                           |
| .byte *b1,...,bn*   | Saves *n*  8-bit literals (b1,...,bn) in consecutive memory                                 |
| .half *h1,...,hn*   | Saves *n* 16-bit literals (h1,...,hn) in consecutive memory                                 |
| .word *w1,...,wn*   | Saves *n* 32-bit literals (w1,...,wn) in consecutive memory                                 |
| .text *[addr]*      | The following lines will be added to the *text* segment and only instructions are expected  |
| .data *[addr]*      | The following lines will be added to the *data* segment and only data is expected           |
| .globl *label*      | It has no logic, it ommits it while parsing the file, added for compatibility reasons       |

# :bulb: Things to be considered

As this implementation is design for a custom CPU, the `.byte`, `.half` and `.word` directives do the same logic,
except that the assembler will complain if it receives a number out of range, this is because each memory address holds 32 bits

