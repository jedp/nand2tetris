// Input file: BasicLoop
// push constant 0    
@0
D=A         // D = 0; Constant 0
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// pop local 0         // initializes sum = 0
// Pop addr LCL + 0
@LCL
D=M         // Base segment local
@0
D=D+A       // Base LCL + offset 0
@R13
M=D         // R13 = base + offset
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@R13
A=M         // A = local 0
M=D         // local 0 = D
// label LOOP_START
(BasicLoop$LOOP_START)
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
// add
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@SP
AM=M-1      // SP--
M=M+D       // D = MEM[SP] + D
@SP         // SP++
AM=M+1
// pop local 0	        // sum = sum + counter
// Pop addr LCL + 0
@LCL
D=M         // Base segment local
@0
D=D+A       // Base LCL + offset 0
@R13
M=D         // R13 = base + offset
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@R13
A=M         // A = local 0
M=D         // local 0 = D
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
// pop argument 0      // counter--
// Pop addr ARG + 0
@ARG
D=M         // Base segment argument
@0
D=D+A       // Base ARG + offset 0
@R13
M=D         // R13 = base + offset
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@R13
A=M         // A = argument 0
M=D         // argument 0 = D
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
// if-goto LOOP_START  // If counter != 0, goto LOOP_START
@SP
AM=M-1      // SP --
D=M         // D = MEM[SP]
@BasicLoop$LOOP_START
D;JNE       // if-goto BasicLoop$LOOP_START
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
// End of input file: BasicLoop
(STOP)
@STOP
0;JMP