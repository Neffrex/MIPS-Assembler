# Main idea
Make a `Two-Pass (Macro?) Assembler`

# Ideas
Implement register aliases as macros [link](https://codebrowser.dev/glibc/glibc/sysdeps/mips/sys/regdef.h.html)
Implementar `address formats` [link](https://www.cs.unibo.it/~solmi/teaching/arch_2002-2003/AssemblyLanguageProgDoc.pdf#page=26)

# Parametros aceptados
Formato del archivo de salida (e.g Conservar etiquetas en forma de comentarios)
Separar segmentos .text y .data en archivos diferentes (Para cargar la RAM y la ROM)


# A decidir
Los datos se guardarán en big o little endian ??
Las direcciones base de los segmentos de datos/texto ?? Dinámicas/Estáticas ??

# Fases de procesamiento
## Fase de precompilado
En esta fase se eliminan los comentarios

En esta fase se interpretan las directivas de precompilado. Estas se señalizan mediante un símbolo `.` inicial.
Estas directivas tienen que tener una `callback function` asociada, que se encargue de la lógica a aplicar en cada caso
`.ascii str`      | Almacena la String (str) en memoria
`.asciiz str`     | Almacena la String (str) en memoria y la termina con el simbolo NULL
`.byte b1,...,bn` | Almacena n literales (b1,...,bn) de 8-bits  en memoria consecutiva
`.half h1,...,hn` | Almacena n literales (h1,...,hn) de 16-bits en memoria consecutiva
`.word w1,...,wn` | Almacena n literales (w1,...,wn) de 32-bits en memoria consecutiva
`.text [addr]`    | Los siguientes elementos formarán parte del segmento de texto,
                  | de haber una dirección (addr) se guardarán a partir de esa dirección y
                  | en este segmento sólo se admiten word(s) e instrucciones
`.data [addr]`    | Los siguientes elementos formarán parte del segmento de datos.
                  | De haber una dirección (addr) se guardarán a partir de esa dirección.

En esta fase también se llenará la `tabla de símbolos` que contendrá la información sobre las etiquetas
Estas se señalizan mediante un símbolo `:` final

En esta fase también se interpretarán las MACROS definidas




