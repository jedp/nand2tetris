#!/usr/bin/env python3

import sys
from vm2hack.parser import Parser


class CompilerConfig:
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

class Compiler:
    def __init__(self, text, config=CompilerConfig()):
        self.input = Parser(text).parse()
        self.config = config
        self.text = []
        self.subs = {}
        self.ret = 0
        self.labels = set("__STOP")

    def compile(self):
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
            self.text += self.subs[label]
        self.asm("// *** End of file ***")

        return '\n'.join(self.text)

    def asm(self, text):
        self.text.append(text)

    def sub(self, text):
        """
        Same as text, but goes at the end of the program for legibility.
        """
        self.subs.append(text)

    def cg(self, cmd):
        if cmd.type == 'Arithmetic':
            if cmd.arg1 == 'add':
                self.cg_add()
                return self.cg_call('__ADD')
            if cmd.arg1 == 'eq':
                self.cg_eq()
                return self.cg_call('__EQ')

        if cmd.type == 'Push':
            return self.cg_push(cmd)

        if cmd.type == 'Pop':
            return self.cg_pop(cmd)

        raise ValueError(f"Unhandled command: {cmd}")

    def cg_push(self, cmd):
        if cmd.arg1 == 'constant':
            value = int(cmd.arg2)
            # Put constant value in D
            self.asm(f"@{value}")
            self.asm("D=A")

        else:
            raise ValueError(r"Unhandled push command: {cmd}")

        # Push D
        self.asm("@SP")
        self.asm("A=M")
        self.asm("M=D")
        # SP++
        self.asm("@SP")
        self.asm("M=M+1")

    def cg_call(self, label):
        ret = f"__RET_{self.ret}"
        self.ret += 1
        self.asm(f"@{ret}")
        self.asm("D=A")
        self.asm("@R15")
        self.asm("M=D")
        self.asm(f"@{label}")
        self.asm("0;JMP")
        self.asm(f"({ret})")

    def cg_add(self):
        if "__ADD" in self.subs:
            return
        sub = []
        sub.append("// *** Subroutine: Add ***")
        sub.append("// *** a = pop; b = pop; d = a + b; push d")
        sub.append("(__ADD)")
        sub.append("// D = MEM[--SP]")
        sub.append("@SP")
        sub.append("M=M-1")
        sub.append("@SP")
        sub.append("A=M")
        sub.append("D=M")
        sub.append("// A = MEM[--SP]")
        sub.append("@SP")
        sub.append("M=M-1")
        sub.append("@SP")
        sub.append("A=M")
        sub.append("// D = Add")
        sub.append("D=D+M")
        sub.append("// MEM[SP++] = D")
        sub.append("@SP")
        sub.append("A=M")
        sub.append("M=D")
        sub.append("@SP")
        sub.append("M=M+1")
        sub.append("// Return")
        sub.append("@R15")
        sub.append("A=M")
        sub.append("0;JMP")
        self.subs["__ADD"] = sub

    def cg_eq(self):
        if "__EQ" in self.subs:
            return
        sub = []
        sub.append("// *** Subroutine: Eq ***")
        sub.append("// a = pop; b = pop; if a == b push -1 else push 0")
        sub.append("(__EQ)")
        sub.append("// D = MEM[--SP]")
        sub.append("@SP")
        sub.append("M=M-1")
        sub.append("@SP")
        sub.append("A=M")
        sub.append("D=M")
        sub.append("// A = MEM[--SP]")
        sub.append("@SP")
        sub.append("M=M-1")
        sub.append("@SP")
        sub.append("A=M")
        sub.append("// If D-M == 0 means a == b")
        sub.append("D=D-M")
        sub.append("@__EQ_RESULT_EQ")
        sub.append("D;JEQ")
        sub.append("// a != b. Store 0 in temp0.")
        sub.append("@{}".format(self.config.temp_base + 0))
        sub.append("M=0")
        sub.append("@__EQ_RETURN_RESULT")
        sub.append("0;JMP")
        sub.append("(__EQ_RESULT_EQ)")
        sub.append("// a == b. Store -1 in temp0.")
        sub.append("@{}".format(self.config.temp_base + 0))
        sub.append("M=-1")
        sub.append("(__EQ_RETURN_RESULT)")
        sub.append("@{}".format(self.config.temp_base + 0))
        sub.append("D=M")
        sub.append("@SP")
        sub.append("A=M")
        sub.append("M=D")
        sub.append("@SP")
        sub.append("M=M+1")
        sub.append("// Return")
        sub.append("@R15")
        sub.append("A=M")
        sub.append("0;JMP")
        self.subs["__EQ"] = sub

    def cg_init(self):
        # Init SP
        self.asm("@{}".format(self.config.stack_base))
        self.asm("D=A")
        self.asm("@SP")
        self.asm("M=D")

    def cg_stop(self):
        self.asm("(__STOP)")
        self.asm("@__STOP")
        self.asm("0;JEQ")


if __name__ == '__main__':
    import sys
    fn = sys.argv[1]

    with open(fn, 'r') as src:
        print(Compiler(src.read()).compile())

