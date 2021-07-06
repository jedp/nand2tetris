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
// Input file: Sys
// function Sys.init 0
(Sys.init)
// push constant 4000	// test THIS and THAT context save
@4000
D=A         // D = 4000; Constant 4000
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// pop pointer 0
@THIS
D=A         // Fixed segment THIS
@0
D=A+D       // Base THIS + offset 0
@R13
M=D
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@R13
A=M
M=D         // Pop and store in fixed segment base THIS + 0
// push constant 5000
@5000
D=A         // D = 5000; Constant 5000
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// pop pointer 1
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
// call Sys.main 0
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
@Sys.main
0;JMP
(Label-1)
// pop temp 1
@5
D=A         // Fixed segment 5
@1
D=A+D       // Base 5 + offset 1
@R13
M=D
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@R13
A=M
M=D         // Pop and store in fixed segment base 5 + 1
// label LOOP
(Sys.init$LOOP)
// goto LOOP
@Sys.init$LOOP
0;JMP
// function Sys.main 5
(Sys.main)
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
@0          // Init arg2 = 0
D=A
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@0          // Init arg3 = 0
D=A
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
@0          // Init arg4 = 0
D=A
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// push constant 4001
@4001
D=A         // D = 4001; Constant 4001
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// pop pointer 0
@THIS
D=A         // Fixed segment THIS
@0
D=A+D       // Base THIS + offset 0
@R13
M=D
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@R13
A=M
M=D         // Pop and store in fixed segment base THIS + 0
// push constant 5001
@5001
D=A         // D = 5001; Constant 5001
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// pop pointer 1
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
// push constant 200
@200
D=A         // D = 200; Constant 200
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// pop local 1
// Pop addr LCL + 1
@LCL
D=M         // Base segment local
@1
D=D+A       // Base LCL + offset 1
@R13
M=D         // R13 = base + offset
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@R13
A=M         // A = local 1
M=D         // local 1 = D
// push constant 40
@40
D=A         // D = 40; Constant 40
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// pop local 2
// Pop addr LCL + 2
@LCL
D=M         // Base segment local
@2
D=D+A       // Base LCL + offset 2
@R13
M=D         // R13 = base + offset
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@R13
A=M         // A = local 2
M=D         // local 2 = D
// push constant 6
@6
D=A         // D = 6; Constant 6
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// pop local 3
// Pop addr LCL + 3
@LCL
D=M         // Base segment local
@3
D=D+A       // Base LCL + offset 3
@R13
M=D         // R13 = base + offset
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@R13
A=M         // A = local 3
M=D         // local 3 = D
// push constant 123
@123
D=A         // D = 123; Constant 123
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// call Sys.add12 1
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
@Sys.add12
0;JMP
(Label-2)
// pop temp 0
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
// push local 2
@LCL
D=M         // local base ptr: LCL
@2
A=D+A       // base LCL + offset 2
D=M         // D = *(addr)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// push local 3
@LCL
D=M         // local base ptr: LCL
@3
A=D+A       // base LCL + offset 3
D=M         // D = *(addr)
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// push local 4
@LCL
D=M         // local base ptr: LCL
@4
A=D+A       // base LCL + offset 4
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
// add
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@SP
AM=M-1      // SP--
M=M+D       // D = MEM[SP] + D
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
// add
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
// function Sys.add12 0
(Sys.add12)
// push constant 4002
@4002
D=A         // D = 4002; Constant 4002
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// pop pointer 0
@THIS
D=A         // Fixed segment THIS
@0
D=A+D       // Base THIS + offset 0
@R13
M=D
@SP
AM=M-1      // SP--
D=M         // D = MEM[SP]
@R13
A=M
M=D         // Pop and store in fixed segment base THIS + 0
// push constant 5002
@5002
D=A         // D = 5002; Constant 5002
@SP         // MEM[SP] = D
AM=M
M=D
@SP         // SP++
AM=M+1
// pop pointer 1
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
// push constant 12
@12
D=A         // D = 12; Constant 12
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
// End of input file: Sys
(STOP)
@STOP
0;JMP