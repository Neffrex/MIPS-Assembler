# What is this proyect?

This is a Two-Pass Assembler for MIPS implemented with Python.

**It is design as an auxiliary programm for a custom implementation of a CPU**

Keep in mind that it doesn't have all the functionality you would expect from a MIPS Assembler.

# :warning: (**WIP**) Customizable options

* Output format (e.g Keep labels in comments)
* Split *data* and *text* segments in different files 
* Define the segments dynamically or statically

# :memo: Valid directives

| Syntax                      | Description                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------  |
| .ascii <*str1, ..., strN*>  | Saves *N* Strings (str1,...,strN) in memory                                                   |
| .asciiz <*str1, ..., strN*> | Saves *N* Strings (str1,...,strN), each one appended with a final *null* value, in memory     |
| .byte <*b1, ..., bN*>       | Saves *N*  8-bit literals (b1,...,bn) in consecutive memory                                   |
| .half <*h1, ..., hN*>       | Saves *N* 16-bit literals (h1,...,hn) in consecutive memory                                   |
| .word <*w1, ..., wN*>       | Saves *N* 32-bit literals (w1,...,wn) in consecutive memory                                   |
| .text *[addr]*              | The following lines will be added to the *text* segment and only instructions are expected, if *addr* is defined the segment will start at that address    |
| .data *[addr]*              | The following lines will be added to the *data* segment and only data is expected, if *addr* is defined the segment will start at that address             |
| .globl <*label*>            | It has no logic, it ommits it while parsing the file, added for compatibility reasons         |

# :bulb: Things to be considered

As this implementation is design for a custom CPU, the `.byte`, `.half` and `.word` directives do the same logic,
except that the assembler will complain if it receives a number out of range, this is because each memory address of the custom CPU holds 32 bits

# :computer: Executing an example

With Python3 already installed and findable on the path, run the following commands inside the directory of this proyect:

```
chmod +x ./assembler-cli.sh
./assembler-cli.sh run examples/mult.asm
```

Another option is to manually execute the main source file with python as follows:

`python3 assembler.py ../assets/ISA.cfg ../examples/mult.asm`

It should generate a file `examples/mult.mem` with the compiled output
