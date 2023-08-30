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
