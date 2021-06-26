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

    def compile(self):
        if self.input['errors']:
            print("ERRORS", file=sys.stderr)
            for err in self.input['errors']:
                print("Line {}: {}".format(err.line, err.msg))
            return ""

        self.cg_init()

        for line in self.input['commands']:
            self.cg(line)

        self.cg_stop()

        return '\n'.join(self.text)

    def asm(self, text):
        self.text.append(text)

    def cg(self, cmd):
        if cmd.type == 'Arithmetic':
            if cmd.arg1 == 'add':
                return self.cg_add(cmd)

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

    def cg_add(self, cmd):
        # SP--
        self.asm("@SP")
        self.asm("M=M-1")
        # D = MEM[SP]
        self.asm("@SP")
        self.asm("A=M")
        self.asm("D=M")
        # SP--
        self.asm("@SP")
        self.asm("M=M-1")
        # A = MEM[SP]
        self.asm("@SP")
        self.asm("A=M")
        # D = Add
        self.asm("D=D+M")

    def cg_init(self):
        # Init SP
        self.asm("@{}".format(self.config.stack_base))
        self.asm("D=A")
        self.asm("@SP")
        self.asm("M=D")

    def cg_stop(self):
        self.asm("@{}".format(len(self.text)))
        self.asm("0;JEQ")


if __name__ == '__main__':
    import sys
    fn = sys.argv[1]

    with open(fn, 'r') as src:
        print(Compiler(src.read()).compile())

