// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Add R0 R1 times. Copy R1 to temp var i so we don't mutate R1.

  @R1
  D=M
  @i      // i = R1
  M=D

  @0      // R2 = 0
  D=A
  @R2
  M=D

(LOOP)
  @i
  D=M
  @STOP
  D;JEQ   // if i==0, break;

  @R0
  D=M
  @R2
  M=M+D   // Add

  @i
  M=M-1   // i = i - 1

  @LOOP
  0;JMP   // Repeat

(STOP)
  // Result already in R2

(END)
  @END
  0;JMP

