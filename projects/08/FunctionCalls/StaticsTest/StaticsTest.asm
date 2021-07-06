// Bootstrap sys
// Set SP=256; call Sys.init.
@256
D=A
@SP
M=D         // SP = 256
// call Sys.init 0
@Label-0
D=A         // D = Label-0; Return address
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@LCL
D=M         // D = *(LCL)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@ARG
D=M         // D = *(ARG)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@THIS
D=M         // D = *(THIS)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@THAT
D=M         // D = *(THAT)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@SP
D=M         // D = SP
@0
D=D-A       // D = SP - nargs
@5
D=D-A       // D = SP - nargs - 5
@ARG
M=D         // Reposition ARG: ARG = SP - nargs - 5
@SP
D=M
@LCL        // Reposition LCL: LCL = SP
M=D
@Sys.init
0;JMP
(Label-0)
// Input file: Class1
// function Class1.set 0
(Class1.set)
// push argument 0
@ARG
D=M         // argument base ptr: ARG
@0
A=D+A       // base ARG + offset 0
D=M         // D = *(addr)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// pop static 0
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@Class1.0
M=D         // Static Class1.0 = D
// push argument 1
@ARG
D=M         // argument base ptr: ARG
@1
A=D+A       // base ARG + offset 1
D=M         // D = *(addr)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// pop static 1
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@Class1.1
M=D         // Static Class1.1 = D
// push constant 0
@0
D=A         // D = 0; Constant 0
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// return
// Save frame in R13
@LCL        // Frame = LCL
D=M
@R13
M=D
@R13
D=M
// Save return address in R14
@5
A=D-A
D=M         // D = *(frame - 5)
@R14
M=D         // Return address = *(frame - 5)
// *ARG = pop()
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@ARG
A=M
M=D         // *ARG = pop()
// SP = ARG + 1
@ARG
D=M+1
@SP
M=D         // SP = ARG + 1
@R13
D=M
@1
A=D-A
D=M
@THAT
M=D         // THAT = *(frame - 1)
@R13
D=M
@2
A=D-A
D=M
@THIS
M=D         // THIS = *(frame - 2)
@R13
D=M
@3
A=D-A
D=M
@ARG
M=D         // ARG = *(frame - 3)
@R13
D=M
@4
A=D-A
D=M
@LCL
M=D         // LCL = *(frame - 4)
@R14
A=M
0;JMP       // goto return address, *(frame - 5)
// function Class1.get 0
(Class1.get)
// push static 0
@Class1.0
D=M
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// push static 1
@Class1.1
D=M
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// sub
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@SP
AM=M-1      // SP--
M=M-D       // D = MEM[SP] - D
@SP         // SP++
AM=M+1
// return
// Save frame in R13
@LCL        // Frame = LCL
D=M
@R13
M=D
@R13
D=M
// Save return address in R14
@5
A=D-A
D=M         // D = *(frame - 5)
@R14
M=D         // Return address = *(frame - 5)
// *ARG = pop()
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@ARG
A=M
M=D         // *ARG = pop()
// SP = ARG + 1
@ARG
D=M+1
@SP
M=D         // SP = ARG + 1
@R13
D=M
@1
A=D-A
D=M
@THAT
M=D         // THAT = *(frame - 1)
@R13
D=M
@2
A=D-A
D=M
@THIS
M=D         // THIS = *(frame - 2)
@R13
D=M
@3
A=D-A
D=M
@ARG
M=D         // ARG = *(frame - 3)
@R13
D=M
@4
A=D-A
D=M
@LCL
M=D         // LCL = *(frame - 4)
@R14
A=M
0;JMP       // goto return address, *(frame - 5)
// End of input file: Class1
// Input file: Sys
// function Sys.init 0
(Sys.init)
// push constant 6
@6
D=A         // D = 6; Constant 6
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// push constant 8
@8
D=A         // D = 8; Constant 8
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// call Class1.set 2
@Label-1
D=A         // D = Label-1; Return address
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@LCL
D=M         // D = *(LCL)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@ARG
D=M         // D = *(ARG)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@THIS
D=M         // D = *(THIS)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@THAT
D=M         // D = *(THAT)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@SP
D=M         // D = SP
@2
D=D-A       // D = SP - nargs
@5
D=D-A       // D = SP - nargs - 5
@ARG
M=D         // Reposition ARG: ARG = SP - nargs - 5
@SP
D=M
@LCL        // Reposition LCL: LCL = SP
M=D
@Class1.set
0;JMP
(Label-1)
// pop temp 0 // Dumps the return value
@5
D=A         // Fixed segment 5
@0
D=A+D       // Base 5 + offset 0
@R13
M=D
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@R13
A=M
M=D         // Pop and store in fixed segment base 5 + 0
// push constant 23
@23
D=A         // D = 23; Constant 23
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// push constant 15
@15
D=A         // D = 15; Constant 15
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// call Class2.set 2
@Label-2
D=A         // D = Label-2; Return address
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@LCL
D=M         // D = *(LCL)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@ARG
D=M         // D = *(ARG)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@THIS
D=M         // D = *(THIS)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@THAT
D=M         // D = *(THAT)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@SP
D=M         // D = SP
@2
D=D-A       // D = SP - nargs
@5
D=D-A       // D = SP - nargs - 5
@ARG
M=D         // Reposition ARG: ARG = SP - nargs - 5
@SP
D=M
@LCL        // Reposition LCL: LCL = SP
M=D
@Class2.set
0;JMP
(Label-2)
// pop temp 0 // Dumps the return value
@5
D=A         // Fixed segment 5
@0
D=A+D       // Base 5 + offset 0
@R13
M=D
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@R13
A=M
M=D         // Pop and store in fixed segment base 5 + 0
// call Class1.get 0
@Label-3
D=A         // D = Label-3; Return address
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@LCL
D=M         // D = *(LCL)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@ARG
D=M         // D = *(ARG)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@THIS
D=M         // D = *(THIS)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@THAT
D=M         // D = *(THAT)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@SP
D=M         // D = SP
@0
D=D-A       // D = SP - nargs
@5
D=D-A       // D = SP - nargs - 5
@ARG
M=D         // Reposition ARG: ARG = SP - nargs - 5
@SP
D=M
@LCL        // Reposition LCL: LCL = SP
M=D
@Class1.get
0;JMP
(Label-3)
// call Class2.get 0
@Label-4
D=A         // D = Label-4; Return address
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@LCL
D=M         // D = *(LCL)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@ARG
D=M         // D = *(ARG)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@THIS
D=M         // D = *(THIS)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@THAT
D=M         // D = *(THAT)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@SP
D=M         // D = SP
@0
D=D-A       // D = SP - nargs
@5
D=D-A       // D = SP - nargs - 5
@ARG
M=D         // Reposition ARG: ARG = SP - nargs - 5
@SP
D=M
@LCL        // Reposition LCL: LCL = SP
M=D
@Class2.get
0;JMP
(Label-4)
// label WHILE
(Sys.init$WHILE)
// goto WHILE
@Sys.init$WHILE
0;JMP
// End of input file: Sys
// Input file: Class2
// function Class2.set 0
(Class2.set)
// push argument 0
@ARG
D=M         // argument base ptr: ARG
@0
A=D+A       // base ARG + offset 0
D=M         // D = *(addr)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// pop static 0
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@Class2.0
M=D         // Static Class2.0 = D
// push argument 1
@ARG
D=M         // argument base ptr: ARG
@1
A=D+A       // base ARG + offset 1
D=M         // D = *(addr)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// pop static 1
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@Class2.1
M=D         // Static Class2.1 = D
// push constant 0
@0
D=A         // D = 0; Constant 0
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// return
// Save frame in R13
@LCL        // Frame = LCL
D=M
@R13
M=D
@R13
D=M
// Save return address in R14
@5
A=D-A
D=M         // D = *(frame - 5)
@R14
M=D         // Return address = *(frame - 5)
// *ARG = pop()
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@ARG
A=M
M=D         // *ARG = pop()
// SP = ARG + 1
@ARG
D=M+1
@SP
M=D         // SP = ARG + 1
@R13
D=M
@1
A=D-A
D=M
@THAT
M=D         // THAT = *(frame - 1)
@R13
D=M
@2
A=D-A
D=M
@THIS
M=D         // THIS = *(frame - 2)
@R13
D=M
@3
A=D-A
D=M
@ARG
M=D         // ARG = *(frame - 3)
@R13
D=M
@4
A=D-A
D=M
@LCL
M=D         // LCL = *(frame - 4)
@R14
A=M
0;JMP       // goto return address, *(frame - 5)
// function Class2.get 0
(Class2.get)
// push static 0
@Class2.0
D=M
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// push static 1
@Class2.1
D=M
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// sub
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@SP
AM=M-1      // SP--
M=M-D       // D = MEM[SP] - D
@SP         // SP++
AM=M+1
// return
// Save frame in R13
@LCL        // Frame = LCL
D=M
@R13
M=D
@R13
D=M
// Save return address in R14
@5
A=D-A
D=M         // D = *(frame - 5)
@R14
M=D         // Return address = *(frame - 5)
// *ARG = pop()
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@ARG
A=M
M=D         // *ARG = pop()
// SP = ARG + 1
@ARG
D=M+1
@SP
M=D         // SP = ARG + 1
@R13
D=M
@1
A=D-A
D=M
@THAT
M=D         // THAT = *(frame - 1)
@R13
D=M
@2
A=D-A
D=M
@THIS
M=D         // THIS = *(frame - 2)
@R13
D=M
@3
A=D-A
D=M
@ARG
M=D         // ARG = *(frame - 3)
@R13
D=M
@4
A=D-A
D=M
@LCL
M=D         // LCL = *(frame - 4)
@R14
A=M
0;JMP       // goto return address, *(frame - 5)
// End of input file: Class2
(STOP)
@STOP
0;JMP