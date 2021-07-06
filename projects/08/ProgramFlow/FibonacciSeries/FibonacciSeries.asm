// Input file: FibonacciSeries
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
// pop pointer 1           // that = argument[1]
@THIS
D=A         // Fixed segment THIS
@1
D=A+D       // Base THIS + offset 1
@R13
M=D
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@R13
A=M
M=D         // Pop and store in fixed segment base THIS + 1
// push constant 0
@0
D=A         // D = 0; Constant 0
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// pop that 0              // first element in the series = 0
// Pop addr THAT + 0
@THAT
D=M         // Base segment that
@0
D=D+A       // Base THAT + offset 0
@R13
M=D         // R13 = base + offset
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@R13
A=M         // A = that 0
M=D         // that 0 = D
// push constant 1
@1
D=A         // D = 1; Constant 1
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// pop that 1              // second element in the series = 1
// Pop addr THAT + 1
@THAT
D=M         // Base segment that
@1
D=D+A       // Base THAT + offset 1
@R13
M=D         // R13 = base + offset
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@R13
A=M         // A = that 1
M=D         // that 1 = D
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
// pop argument 0          // num_of_elements -= 2 (first 2 elements are set)
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
// label MAIN_LOOP_START
(FibonacciSeries$MAIN_LOOP_START)
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
// if-goto COMPUTE_ELEMENT // if num_of_elements > 0, goto COMPUTE_ELEMENT
@SP
AM=M-1      // SP --
D=M         // D = MEM[SP]
@FibonacciSeries$COMPUTE_ELEMENT
D;JNE       // if-goto FibonacciSeries$COMPUTE_ELEMENT
// goto END_PROGRAM        // otherwise, goto END_PROGRAM
@FibonacciSeries$END_PROGRAM
0;JMP
// label COMPUTE_ELEMENT
(FibonacciSeries$COMPUTE_ELEMENT)
// push that 0
@THAT
D=M         // that base ptr: THAT
@0
A=D+A       // base THAT + offset 0
D=M         // D = *(addr)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// push that 1
@THAT
D=M         // that base ptr: THAT
@1
A=D+A       // base THAT + offset 1
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
// pop that 2              // that[2] = that[0] + that[1]
// Pop addr THAT + 2
@THAT
D=M         // Base segment that
@2
D=D+A       // Base THAT + offset 2
@R13
M=D         // R13 = base + offset
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@R13
A=M         // A = that 2
M=D         // that 2 = D
// push pointer 1
@THIS
D=A         // Base fixed segment THIS
@1
A=A+D       // Base THIS + offset 1
D=M
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
// add
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@SP
AM=M-1      // SP--
M=M+D       // D = MEM[SP] + D
@SP         // SP++
AM=M+1
// pop pointer 1           // that += 1
@THIS
D=A         // Fixed segment THIS
@1
D=A+D       // Base THIS + offset 1
@R13
M=D
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@R13
A=M
M=D         // Pop and store in fixed segment base THIS + 1
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
// pop argument 0          // num_of_elements--
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
// goto MAIN_LOOP_START
@FibonacciSeries$MAIN_LOOP_START
0;JMP
// label END_PROGRAM
(FibonacciSeries$END_PROGRAM)
// End of input file: FibonacciSeries
(STOP)
@STOP
0;JMP