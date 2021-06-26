#!/usr/bin/env python3

import sys
from vm2hack.parser import Parser


def unindent(text):
    """
    Unindent a multiline string up to and including the '|' character.
    """
    lines = text.strip().splitlines()
    return '\n'.join([line.split('|')[1] for line in lines])


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

    def cg_call(self, label):
        ret = f"__RET_{self.ret}"
        self.ret += 1
        self.asm(unindent(f"""
            |@{ret}
            |D=A
            |@R15
            |M=D
            |@{label}
            |0;JMP
            |({ret})
            """))

    def cg_add(self):
        if "__ADD" in self.subs:
            return
        self.subs["__ADD"] = unindent("""
            |// *** Subroutine: Add ***
            |// *** a = pop; b = pop; d = a + b; push d
            |(__ADD)
            |// D = MEM[--SP]
            |@SP
            |M=M-1
            |@SP
            |A=M
            |D=M
            |// A = MEM[--SP]
            |@SP
            |M=M-1
            |@SP
            |A=M
            |// D = Add
            |D=D+M
            |// MEM[SP++] = D
            |@SP
            |A=M
            |M=D
            |@SP
            |M=M+1
            |// Return
            |@R15
            |A=M
            |0;JMP
            """)

    def cg_eq(self):
        if "__EQ" in self.subs:
            return
        temp0 = self.config.temp_base
        self.subs["__EQ"] = unindent(f"""
            |// *** Subroutine: Eq ***
            |// a = pop; b = pop; if a == b push -1 else push 0
            |(__EQ)
            |// D = MEM[--SP]
            |@SP
            |M=M-1
            |@SP
            |A=M
            |D=M
            |// A = MEM[--SP]
            |@SP
            |M=M-1
            |@SP
            |A=M
            |// If D-M == 0 means a == b
            |D=D-M
            |@__EQ_RESULT_EQ
            |D;JEQ
            |// a != b. Store 0 in temp0.
            |@{temp0}
            |M=0
            |@__EQ_RETURN_RESULT
            |0;JMP
            |(__EQ_RESULT_EQ)
            |// a == b. Store -1 in temp0.
            |@{temp0}
            |M=-1
            |(__EQ_RETURN_RESULT)
            |@{temp0}
            |D=M
            |@SP
            |A=M
            |M=D
            |@SP
            |M=M+1
            |// Return
            |@R15
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
    import sys
    fn = sys.argv[1]

    with open(fn, 'r') as src:
        print(Compiler(src.read()).compile())

