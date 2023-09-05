# What is this proyect?
This is a Two-Pass Assembler for MIPS implemented with Python.
**It is design as an auxiliary programm for a custom implementation of a CPU**
Keep in mind that it doesn't have all the functionality you would expect from a MIPS Assembler.

# (**WIP**) Customizable options
* Output format (e.g Keep labels in comments)
* Split *data* and *text* segments in different files 
* Define the segments dynamically or statically

# Valid directives
`.ascii str`      | Saves the String (str) in memory
`.asciiz str`     | Saves the String (str), appending a final *null* value, in memory
`.byte b1,...,bn` | Saves *n*  8-bit literals (b1,...,bn) in consecutive memory
`.half h1,...,hn` | Saves *n* 16-bit literals (h1,...,hn) in consecutive memory
`.word w1,...,wn` | Saves *n* 32-bit literals (w1,...,wn) in consecutive memory
`.text [addr]`    | Los siguientes elementos formarán parte del segmento de texto,
                  | de haber una dirección (addr) se guardarán a partir de esa dirección y
                  | en este segmento sólo se admiten word(s) e instrucciones
`.data [addr]`    | Los siguientes elementos formarán parte del segmento de datos.
                  | De haber una dirección (addr) se guardarán a partir de esa dirección.
`.globl label`    | Actualmente no tiene ninguna lógica, ya que el programa no 
                  | está diseñado para ser compatible con un linker

# Things to be considered
As this implementation is design for a custom CPU, the `.byte`, `.half` and `.word` directives do the same logic,
except that the assembler will complain if it receives a number out of range, this is because each memory address holds 32 bits

