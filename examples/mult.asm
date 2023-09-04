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
#Utiliza las instrucciones: lw, sw, and, add, slt y beq

.text
.globl main

#main: inicio del programa
#   registros: 	$zero -&gt; 0d = 0h
#		$t1 -&gt; 9d = 9h
#		$a0 -&gt; 4d = 4h
#		$a1 -&gt; 5d = 5h
#		$s0 -&gt; 16d = 10h
#		$s1 -&gt; 17d = 11h

main:   
   lw   $t1, 100($zero)   # carga la constante "1"
   lw   $a0, 101($zero)   # carga el valor de a
   lw   $a1, 102($zero)   # carga el valor de b

   and  $s0, $zero, $zero  # s := 0
   and  $s1, $zero, $zero  # i := 0

per:

   slt  $t0, $s1, $a0       # i < a ?
   beq  $t0, $zero, fiper   # si $t0 = 0 pc = fiper          

   add  $s0, $s0, $a1   # s := s + b
   add  $s1, $s1, $t1   # i := i + 1

   beq  $zero, $zero, per   # jump per 

fiper:

   sw $s0, 103($zero)    # salva s

fi:
   beq $zero, $zero, fi # bucle infinito


.data 

uno: .word 1
a: .word 3
b: .word 5
s: .asciiz "x"
