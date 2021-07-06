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
// Input file: Main
// function Main.fibonacci 0
(Main.fibonacci)
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
// push constant 2
@2
D=A         // D = 2; Constant 2
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// lt                     // checks if n<2
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@SP
AM=M-1      // SP--
D=M-D
@Label-1-cmp-lt
D;JLT     // Comparing x lt y, so x-y;JLT
@SP
AM=M
M=0         // !lt: MEM[SP] = 0 (false)
@Label-2-cmp-done
0;JMP
(Label-1-cmp-lt)
@SP
AM=M
M=-1        // lt: MEM[SP] = -1 (true)
(Label-2-cmp-done)
@SP
AM=M+1      // SP++
// if-goto IF_TRUE
@SP
AM=M-1      // SP --
D=M         // D = MEM[SP]
@Main.fibonacci$IF_TRUE
D;JNE       // if-goto Main.fibonacci$IF_TRUE
// goto IF_FALSE
@Main.fibonacci$IF_FALSE
0;JMP
// label IF_TRUE          // if n<2, return n
(Main.fibonacci$IF_TRUE)
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
// label IF_FALSE         // if n>=2, returns fib(n-2)+fib(n-1)
(Main.fibonacci$IF_FALSE)
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
// push constant 2
@2
D=A         // D = 2; Constant 2
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
// call Main.fibonacci 1  // computes fib(n-2)
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
@1
D=D-A       // D = SP - nargs
@5
D=D-A       // D = SP - nargs - 5
@ARG
M=D         // Reposition ARG: ARG = SP - nargs - 5
@SP
D=M
@LCL        // Reposition LCL: LCL = SP
M=D
@Main.fibonacci
0;JMP
(Label-3)
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
// push constant 1
@1
D=A         // D = 1; Constant 1
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
// call Main.fibonacci 1  // computes fib(n-1)
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
@1
D=D-A       // D = SP - nargs
@5
D=D-A       // D = SP - nargs - 5
@ARG
M=D         // Reposition ARG: ARG = SP - nargs - 5
@SP
D=M
@LCL        // Reposition LCL: LCL = SP
M=D
@Main.fibonacci
0;JMP
(Label-4)
// add                    // returns fib(n-1) + fib(n-2)
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@SP
AM=M-1      // SP--
M=M+D       // D = MEM[SP] + D
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
// End of input file: Main
// Input file: Sys
// function Sys.init 0
(Sys.init)
// push constant 4
@4
D=A         // D = 4; Constant 4
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// call Main.fibonacci 1   // computes the 4'th fibonacci element
@Label-5
D=A         // D = Label-5; Return address
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
@1
D=D-A       // D = SP - nargs
@5
D=D-A       // D = SP - nargs - 5
@ARG
M=D         // Reposition ARG: ARG = SP - nargs - 5
@SP
D=M
@LCL        // Reposition LCL: LCL = SP
M=D
@Main.fibonacci
0;JMP
(Label-5)
// label WHILE
(Sys.init$WHILE)
// goto WHILE              // loops infinitely
@Sys.init$WHILE
0;JMP
// End of input file: Sys
(STOP)
@STOP
0;JMP