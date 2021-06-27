#!/usr/bin/env python3

import sys
from vm2hack.parser import Parser


ARG_ADD = 1
ARG_SUB = 2
ARG_AND = 3
ARG_OR  = 4
ARG_NEG = 0
ARG_NOT = 1

def unindent(text):
    """
    Unindent a multiline string up to and including the '|' character.
    """
    lines = text.strip().splitlines()
    return '\n'.join([line.split('|')[1] for line in lines])

class Config:
    def __init__(self,
            sp=0,
            lcl=1,
            arg=2,
            this=3,
            that=4,
            temp_base=5,
            r13=13,
            r14=14,
            r15=15,
            static_base=16,
            stack_base=256):
        self.sp = sp
        self.lcl = lcl
        self.arg = arg
        self.this = this
        self.that = that
        self.temp_base = temp_base
        self.r13 = r13
        self.r14 = r14
        self.r15 = r15
        self.static_base = static_base
        self.stack_base = stack_base

class CodeWriter:
    def __init__(self, text, ns, config=Config()):
        self.input = Parser(text).parse()
        self.config = config
        self.text = []
        self.ns = ns
        self.subs = {}
        self.ret = 0
        self.labels = set("__STOP")

    def genCode(self):
        if self.input['errors']:
            print("ERRORS", file=sys.stderr)
            for err in self.input['errors']:
                print("Line {}: {}".format(err.line, err.msg))
            return ""

        # Init variables and environment.
        self.cg_init()

        # Translate input.
        for cmd in self.input['commands']:
            # Print original VM command as a comment.
            self.asm('// ' + cmd.src)
            self.cg(cmd)

        # Add the stop loop.
        self.asm("// *** STOP loop ***")
        self.cg_stop()

        # Add all the subroutines that were generated.
        self.asm('// *** Subroutines ***')
        for label in self.subs:
            self.text += self.subs[label].splitlines()
        self.asm("// *** End of file ***")

        return '\n'.join(self.text)

    def asm(self, text):
        self.text.append(text)

    def sub(self, text):
        """
        Same as text, but goes at the end of the program for legibility.
        """
        self.subs.append(text)

    def nextRet(self):
        ret = f"__RET_{self.ret}"
        self.ret += 1
        return ret

    def cg(self, cmd):
        if cmd.type == 'Arithmetic':
            self.cg_binop_popxy()
            self.cg_arith()
            self.cg_monop()
            self.cg_cmp()
            if cmd.arg1 in ['add', 'sub', 'and', 'or']:
                return self.cg_call_arith(cmd.arg1)
            if cmd.arg1 in ['neg', 'not']:
                return self.cg_call_monop(cmd.arg1)
            if cmd.arg1 in ['lt', 'eq', 'gt']:
                return self.cg_call_cmp(cmd.arg1)

        if cmd.type == 'Push':
            return self.cg_push(cmd)

        if cmd.type == 'Pop':
            return self.cg_pop(cmd)

        raise ValueError(f"Unhandled command: {cmd}")

    def cg_push(self, cmd):
        if cmd.arg1 == 'constant':
            value = int(cmd.arg2)
            self.asm(f"@{value}")
            self.asm("D=A")

        else:
            raise ValueError(r"Unhandled push command: {cmd}")

        self.asm(unindent("""
            |// MEM[SP++] = D
            |@SP
            |A=M
            |M=D
            |@SP
            |M=M+1
            """))

    def cg_call_cmp(self, fn):
        if fn == 'lt':
            arg = -1
        elif fn == 'eq':
            arg = 0
        elif fn == 'gt':
            arg = 1
        else:
            raise ValueError(f"Unknown cmp function: {fn}")
        self.cg_call('__CMP', arg)

    def cg_call_monop(self, fn):
        if fn == 'neg':
            arg = ARG_NEG
        elif fn == 'not':
            arg = ARG_NOT
        else:
            raise ValueError(f"Unknown monop: {fn}")
        self.cg_call('__UNARY', arg)

    def cg_call_arith(self, fn):
        if fn == 'add':
            arg = ARG_ADD
        elif fn == 'sub':
            arg = ARG_SUB
        elif fn == 'and':
            arg = ARG_AND
        elif fn == 'or':
            arg = ARG_OR
        else:
            raise ValueError(f"Unknown function: {fn}")
        self.cg_call('__ARITHMETIC', arg)

    def cg_call(self, label, arg):
        """
        Call a function with a single primitive numeric argument.

        Label is label to jump to.
        """
        ret = self.nextRet()
        if arg < 0:
            argstr = str(32768 + arg)
        else:
            argstr = str(arg)
        self.asm(unindent(f"""
            |@{ret}
            |D=A
            |@R15
            |M=D
            |@{argstr}
            |D=A
            |@R13
            |M=D
            |@{label}
            |0;JMP
            |({ret})
            """))

    def cg_binop_popxy(self):
        """
        A reusable snippet for capturing x and y from the top of the stack.

        Mutates the stack and sets variables:
        R14 = pop y
        R13 = pop x

        Return to address in R15.
        """
        if '__GET_XY' in self.subs:
            return
        self.subs['__GET_XY'] = unindent("""
            |// *** R14 = pop y, R13 = pop x; Jump to R15
            |(__GET_XY)
            |@SP            // pop y:
            |M=M-1          // --SP
            |@SP
            |A=M
            |D=M
            |@R14
            |M=D            // R14 = MEM[SP]
            |@SP            // pop x
            |M=M-1          // --SP
            |@SP
            |A=M
            |D=M
            |@R13
            |M=D            // R13 = MEM[SP]
            |@R15           // Return to @R15
            |A=M
            |0;JEQ
            """)

    def cg_monop(self):
        """
        Routine to perform unary operations Neg and Not.

        Args:
        R13: 0 for neg, 1 for not
        R15: Return address

        Stack:
        x = pop
        push op x
        """
        if '__UNARY' in self.subs:
            return
        temp0 = self.config.temp_base
        temp1 = self.config.temp_base + 1
        temp7 = self.config.temp_base + 7
        self.subs['__UNARY'] = unindent(f"""
            |// *** Subroutine: Unary operator arithmetic function ***
            |// x = pop; push op x
            |// Caller set function in R13:
            |// R13 = 0 for neg, 1 for not
            |// R15 = return address
            |(__UNARY)
            |@R15
            |D=M
            |@{temp7}       // Store return address in temp7
            |M=D
            |@SP            // x = MEM[--SP]
            |M=M-1
            |@SP
            |A=M
            |D=M
            |@{temp0}       // Store x in temp0
            |M=D
            |@R13           // Switch on requested function.
            |D=M
            |@__UNARY_NEG
            |D;JEQ          // Jump to Neg
            |               // Fall through to Not
            |@{temp0}       // Load x
            |D=M
            |@{temp1}       // Store !x in temp1
            |M=!D
            |@__UNARY_RETURN_RESULT
            |0;JEQ
            |
            |(__UNARY_NEG)
            |@{temp0}
            |D=M
            |@{temp1}       // Store -x in temp1
            |M=-D
            |               // Fall through to return result
            |(__UNARY_RETURN_RESULT)
            |@{temp1}
            |D=M
            |@SP            // MEM[SP++] = temp1
            |A=M
            |M=D
            |@SP
            |M=M+1
            |@{temp7}       // Return
            |A=M
            |0;JMP
            """)

    def cg_arith(self):
        """
        Routine to perform addition or subtraction.

        Args:
        R13 ID for Add, Sub, And, or Or
        R15 Return address

        Stack:
        y = pop
        x = pop
        push x fn y
        """
        if '__ARITHMETIC' in self.subs:
            return
        temp0 = self.config.temp_base
        temp1 = self.config.temp_base + 1
        temp7 = self.config.temp_base + 7
        self.subs['__ARITHMETIC'] = unindent(f"""
            |// *** Subroutine: Binary operator arithmetic function ***
            |// a = pop; b = pop; d = a op b; push d
            |// Caller sets function in R13:
            |// R13 = ID of function (add, sub, and, or)
            |// R15 = return address
            |(__ARITHMETIC)
            |@R15
            |D=M
            |@{temp7}       // Store return address in temp7.
            |M=D
            |@R13
            |D=M
            |@{temp1}       // Store func choice in temp1.
            |M=D
            |@__ARITH_FN    // Push return address for get-xy.
            |D=A
            |@R15
            |M=D
            |@__GET_XY      // Get x and y.
            |0;JMP
            |(__ARITH_FN)   // Now R13=x, R14=y.
            |
            |@{temp1}       // Switch on temp1 to find the right function.
            |D=M
            |@{ARG_ADD}
            |D=D-A
            |@__ARITH_ADD
            |D;JEQ          // goto Add
            |
            |@{temp1}
            |D=M
            |@{ARG_SUB}
            |D=D-A
            |@__ARITH_SUB
            |D;JEQ          // goto Sub
            |
            |@{temp1}
            |D=M
            |@{ARG_AND}
            |D=D-A
            |@__ARITH_AND
            |D;JEQ          // goto And
            |
            |               // Else fall through to Or.
            |
            |@R13           // x from get-xy
            |D=M
            |@R14           // y from get-xy
            |A=M
            |D=D|A
            |@{temp0}       // Store x|y in temp0.
            |M=D
            |@__ARITH_STORE_RESULT
            |0;JMP          // goto return result
            |
            |(__ARITH_AND)
            |@R13           // x
            |D=M
            |@R14           // y
            |A=M
            |D=D&A
            |@{temp0}       // Store x&y in temp0.
            |M=D
            |@__ARITH_STORE_RESULT
            |0;JMP          // goto return result
            |
            |(__ARITH_SUB)
            |@R13           // x
            |D=M
            |@R14           // y
            |A=M
            |D=D-A
            |@{temp0}       // Store x-y in temp0.
            |M=D
            |@__ARITH_STORE_RESULT
            |0;JMP          // goto return result
            |
            |(__ARITH_ADD)
            |@R13           // x
            |D=M
            |@R14           // y
            |A=M
            |D=D+A
            |@{temp0}       // Store x+y in temp0.
            |M=D            // Fall through to store result.
            |
            |(__ARITH_STORE_RESULT)
            |@{temp0}
            |D=M
            |@SP            // MEM[SP] = x+y
            |A=M
            |M=D
            |@SP
            |M=M+1          // SP++
            |@{temp7}       // Return
            |A=M
            |0;JMP
            """)

    def cg_cmp(self):
        """
        Routine to perform comparisons (lt, eq, gt).

        Args:
        R13 = -1 for lt, 0 for eq, 1 for gt
        R15 = return address

        Stack:
        y = pop
        x = pop
        push x cmp y
        """
        if '__CMP' in self.subs:
            return
        temp0 = self.config.temp_base
        temp1 = self.config.temp_base + 1
        temp7 = self.config.temp_base + 7
        self.subs['__CMP'] = unindent(f"""
            |// *** Subroutine: Compare ***
            |// y = pop; x = pop; if x cmp y push -1 else push 0
            |// Caller sets comparison function in R13:
            |// R13 = -1 ==> lt
            |// R13 =  0 ==> eq
            |// R13 =  1 ==> gt
            |// R15 = return address
            |(__CMP)
            |@R15
            |D=M
            |@{temp7}       // Store return address in temp7.
            |M=D
            |@R13
            |D=M
            |@{temp1}       // Store comparison function in temp1.
            |M=D
            |@__CMP_XY
            |D=A
            |@R15
            |M=D
            |@__GET_XY      // Get x and y from stack.
            |0;JEQ
            |(__CMP_XY)     // Now R13=x, R14=y
            |
            |@{temp1}
            |D=M            // Which comparison function.
            |@__CMP_LT
            |D;JLT          // Jump to compare lt?
            |
            |@__CMP_GT
            |D;JGT          // Jump to compare gt?
            |               // Fall through to compare eq.
            |(__CMP_EQ)     // Compare: EQ
            |@R14           // y
            |D=M
            |@R13           // x
            |D=M-D          // If x eq y, then D=M-D == 0
            |@__CMP_STORE_TRUE
            |D;JEQ
            |@__CMP_STORE_FALSE
            |0;JMP
            |
            |(__CMP_LT)     // Compare: x lt y?
            |@R14           // y
            |D=M
            |@R13           // x
            |D=M-D          // If x < y, then D=M-D < 0
            |@__CMP_STORE_TRUE
            |D;JLT
            |@__CMP_STORE_FALSE
            |0;JMP
            |
            |(__CMP_GT)     // Compare: GT
            |@R14           // y
            |D=M
            |@R13           // x
            |D=M-D          // If x > y, then D=M-D > 0
            |@__CMP_STORE_TRUE
            |D;JLT          // If not true, fall through to store false.
            |
            |(__CMP_STORE_FALSE)
            |@{temp0}
            |M=0            // x not cmp y. Store 0 (false) in temp0.
            |@__CMP_RETURN_RESULT
            |0;JMP
            |(__CMP_STORE_TRUE)
            |@{temp0}
            |M=-1           // x cmp y. Store -1 (true) in temp0
            |(__CMP_RETURN_RESULT)
            |@{temp0}
            |D=M
            |@SP
            |A=M
            |M=D            // Push temp0 val on stack.
            |@SP
            |M=M+1
            |@{temp7}       // Return
            |A=M
            |0;JMP
            """)

    def cg_init(self):
        self.asm(unindent("""
            |// SP = 0
            |@{}
            |D=A
            |@SP
            |M=D
            """.format(self.config.stack_base)))

    def cg_stop(self):
        self.asm(unindent("""
            |(__STOP)
            |@__STOP
            |0;JEQ
            """))


if __name__ == '__main__':
    import os
    import sys

    fn = sys.argv[1]
    ns = os.path.split(fn)[-1].split('.')[0]

    with open(fn, 'r') as src:
        print(CodeWriter(src.read(), ns).genCode())

