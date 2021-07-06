// Input file: SimpleFunction
// function SimpleFunction.test 2
(SimpleFunction.test)
@0          // Init arg0 = 0
D=A
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@0          // Init arg1 = 0
D=A
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// push local 0
@LCL
D=M         // local base ptr: LCL
@0
A=D+A       // base LCL + offset 0
D=M         // D = *(addr)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// push local 1
@LCL
D=M         // local base ptr: LCL
@1
A=D+A       // base LCL + offset 1
D=M         // D = *(addr)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// add
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@SP
AM=M-1      // SP--
M=M+D       // D = MEM[SP] + D
@SP         // SP++
AM=M+1
// not
@SP
AM=M-1      // SP--
D=!M        // D = MEM[SP]
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
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
// add
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@SP
AM=M-1      // SP--
M=M+D       // D = MEM[SP] + D
@SP         // SP++
AM=M+1
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
// End of input file: SimpleFunction
(STOP)
@STOP
0;JMP