#!/usr/bin/env python3

import sys
from vm2hack.parser import Parser


def unindent(text):
    """
    Unindent a multiline string up to and including the '|' character.
    """
    lines = text.strip().splitlines()
    return '\n'.join([line.strip() for line in lines if line.strip()])

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

        # Mapping of vm word to asm register.
        self.segments = {
            'local': 'LCL',
            'argument': 'ARG',
            'this': 'THIS',
            'that': 'THAT'
        }

class CodeWriter:
    """
    Read Hack vm source and convert it to asm.
    """

    def __init__(self, vm_code, ns, config=Config()):
        self.input = Parser(vm_code).parse()
        self.config = config
        self.text = []
        self.ns = ns
        self.next_static = 0
        self.next_label = 0
        self.static_offsets = {}

    def genCode(self):
        """
        Generate the complete asm output.
        """
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

        return '\n'.join(self.text)

    def asm(self, text):
        """
        Helper function to add asm text.
        """
        self.text.append(text)

    def uniqueLabel(self):
        """
        Generate a unique label for jumps.
        """
        label = f"__L{self.next_label}"
        self.next_label += 1
        return label

    def cg(self, cmd):
        """
        Handle a command and generate the asm for it.
        """
        if cmd.type == 'Arithmetic':
            if cmd.arg1 in ['add', 'sub', 'and', 'or']:
                return self.cg_inline_arith(cmd.arg1)
            if cmd.arg1 in ['neg', 'not']:
                return self.cg_inline_unary(cmd.arg1)
            if cmd.arg1 in ['lt', 'eq', 'gt']:
                return self.cg_inline_cmp(cmd.arg1)

        if cmd.type == 'Push':
            if cmd.arg1 == 'constant':
                return self.cg_push_constant(cmd)
            if cmd.arg1 in ['argument', 'local', 'this', 'that']:
                return self.cg_push_segment(cmd)
            if cmd.arg1 == 'temp':
                return self.cg_push_temp(cmd)
            if cmd.arg1 == 'pointer':
                return self.cg_push_pointer(cmd)
            if cmd.arg1 == 'static':
                return self.cg_push_static(cmd)

        if cmd.type == 'Pop':
            if cmd.arg1 == 'constant':
                raise ValueError(f"Syntax error. Cannot pop constant: {cmd}")
            if cmd.arg1 in ['argument', 'local', 'this', 'that']:
                return self.cg_pop_segment(cmd)
            if cmd.arg1 == 'temp':
                return self.cg_pop_temp(cmd)
            if cmd.arg1 == 'pointer':
                return self.cg_pop_pointer(cmd)
            if cmd.arg1 == 'static':
                return self.cg_pop_static(cmd)

        raise ValueError(f"Unhandled command: {cmd}")

    def cg_push_constant(self, cmd):
        """
        Push a constant value on the stack.

        Value must be positive, unsigned int between 0 and 32767.
        """
        assert(cmd.arg1 == 'constant')
        self.asm(unindent(f"""
            @{cmd.arg2}     // Constant {cmd.arg2}
            D=A             // D = {cmd.arg2}
            @SP             // MEM[SP] = D
            A=M
            M=D
            @SP             // SP++
            M=M+1
            """))

    def cg_push_segment(self, cmd):
        """
        Get value at segment+offset and push it on the stack.
        """
        assert(cmd.arg1 in self.config.segments)
        base_ptr = self.config.segments[cmd.arg1]
        offset = int(cmd.arg2)
        self.asm(unindent(f"""
            @{base_ptr}     // {cmd.arg1} base ptr: {base_ptr}
            D=M
            @{offset}       // offset: {offset}
            D=D+A           // D = addr of {cmd.arg1} {cmd.arg2}
            A=D
            D=M             // D = value at addr {cmd.arg1} {cmd.arg2}
            @SP
            A=M
            M=D             // MEM[SP] = D
            @SP
            M=M+1           // SP++
            """))

    def cg_pop_segment(self, cmd):
        """
        Pop and store in segment+offset.
        """
        assert(cmd.arg1 in self.config.segments)
        base_ptr = self.config.segments[cmd.arg1]
        offset = int(cmd.arg2)
        self.asm(unindent(f"""
            @{base_ptr}     // {cmd.arg1} base ptr: {base_ptr}
            D=M
            @{offset}       // offset: {offset}
            D=D+A           // D = {cmd.arg1} {cmd.arg2}
            @R13
            M=D             // Stash address. R13 = D
            @SP
            AM=M-1          // SP--
            D=M             // D = MEM[SP]
            @R13
            A=M             // A = {cmd.arg1} {cmd.arg2}
            M=D             // {cmd.arg1} {cmd.arg2} = D
            """))

    def cg_push_temp(self, cmd):
        """
        Get from temp segment at offset and push onto stack.
        """
        assert(cmd.arg1 == 'temp')
        addr = self.config.temp_base + int(cmd.arg2)
        self.asm(unindent(f"""
            @{addr}         // Temp base + offset {cmd.arg2}
            D=M
            @SP
            A=M
            M=D             // MEM[SP] = value at temp + offset {cmd.arg2}
            @SP
            M=M+1           // SP++
            """))

    def cg_pop_temp(self, cmd):
        """
        Pop and store at offset in temp segment.
        """
        assert(cmd.arg1 == 'temp')
        addr = self.config.temp_base + int(cmd.arg2)
        self.asm(unindent(f"""
            @SP
            AM=M-1          // SP--
            D=M             // D = MEM[SP]
            @{addr}         // Temp base + offset {cmd.arg2}
            M=D             // Temp {cmd.arg2} = D
            """))

    def cg_push_pointer(self, cmd):
        """
        Push the address of pointer 0 or 1 on the stack.
        """
        assert(cmd.arg1 == 'pointer')
        if cmd.arg2 == '0':
            addr = self.config.this
        elif cmd.arg2 == '1':
            addr = self.config.that
        else:
            raise ValueError(f"Bad pointer for push: {cmd}")
        self.asm(unindent(f"""
            @{addr}         // Pointer {cmd.arg2} addr
            D=M
            @SP
            A=M
            M=D             // MEM[SP] = value at pointer {cmd.arg2}
            @SP
            M=M+1           // SP++
            """))

    def cg_pop_pointer(self, cmd):
        """
        Pop a value and write it as the address of pointer 0 or 1.
        """
        assert(cmd.arg1 == 'pointer')
        if cmd.arg2 == '0':
            addr = self.config.this
        elif cmd.arg2 == '1':
            addr = self.config.that
        else:
            raise ValueError(f"Bad pointer for pop: {cmd}")
        self.asm(unindent(f"""
            @SP
            AM=M-1          // SP--
            D=M             // D = MEM[SP]
            @{addr}         // Pointer {cmd.arg2} addr
            M=D             // Pointer {cmd.arg2} = D
            """))

    def staticAddress(self, arg):
        """
        Get a static variable offset for the given static arg.
        """
        label = self.ns + '.' + arg
        if label not in self.static_offsets:
            self.static_offsets[label] = self.next_static
            self.next_static += 1
        base = self.config.static_base
        offset = self.static_offsets[label]
        return base + offset

    def cg_push_static(self, cmd):
        """
        Push the given static variable onto the stack.
        """
        assert(cmd.arg1 == 'static')
        addr = self.staticAddress(cmd.arg2)
        self.asm(unindent(f"""
            @{addr}         // Static addr {cmd.arg2} in {self.ns}
            D=M
            @SP
            A=M
            M=D             // MEM[SP] = value at static address {addr}
            @SP
            M=M+1           // SP++
            """))

    def cg_pop_static(self, cmd):
        """
        Pop the stack and store the value in the given static variable.
        """
        assert(cmd.arg1 == 'static')
        addr = self.staticAddress(cmd.arg2)
        self.asm(unindent(f"""
            @SP
            AM=M-1          // SP--
            D=M             // D = MEM[SP]
            @{addr}         // Static addr {cmd.arg2} in {self.ns}
            M=D             // Static = D
            """))

    def cg_inline_cmp(self, fn):
        """
        Pop two values and push the result of the given comparision.

        True is -1, false is 0.
        """
        if fn == 'lt':
            jmp = 'JGT'
        elif fn == 'eq':
            jmp = 'JEQ'
        elif fn == 'gt':
            jmp = 'JLT'
        else:
            raise ValueError(f"Unknown cmp function: {fn}")
        true_branch = self.uniqueLabel()
        store_result = self.uniqueLabel()
        self.asm(unindent(f"""
            @SP
            AM=M-1      // SP--
            D=M         // D = MEM[SP]
            @SP
            AM=M-1      // SP--
            D=D-M
            @{true_branch}
            D;{jmp}     // Comparing x {fn} y, so x-y;{jmp}
            D=0         // Result = 0 (false)
            @{store_result}
            0;JEQ
            ({true_branch})
            D=-1        // Result = -1 (true)
            ({store_result})
            @SP
            A=M
            M=D         // MEM[SP] = result
            @SP
            M=M+1       // SP++
            """))

    def cg_inline_unary(self, fn):
        """
        Pop a value and push the result of the given unary operation.
        """
        if fn == 'neg':
            op = '-'
        elif fn == 'not':
            op = '!'
        else:
            raise ValueError(f"Unknown unary operator: {fn}")
        self.asm(unindent(f"""
            @SP
            AM=M-1      // SP--
            D={op}M     // D = MEM[SP]
            @SP
            A=M
            M=D
            @SP
            M=M+1       // SP++
            """))

    def cg_inline_arith(self, fn):
        """
        Generate code to do arithmetic on the stack.

        Pop two values and push the result of the operation on them.
        """
        if fn == 'add':
            op = '+'
        elif fn == 'sub':
            op = '-'
        elif fn == 'and':
            op = '&'
        elif fn == 'or':
            op = '|'
        else:
            raise ValueError(f"Unknown arithmetic function: {fn}")
        self.asm(unindent(f"""
            @SP
            AM=M-1      // SP--
            D=M         // D = MEM[SP]
            @SP
            AM=M-1      // SP--
            D=M{op}D
            @SP
            A=M
            M=D
            @SP
            M=M+1
            """))

    def cg_init(self):
        """
        Init the contents of the segment pointer registers.
        Keep an eye on whether this starts to conflict with the tst scripts.
        """
        self.asm(unindent("""
            // SP = 0
            @{}
            D=A
            @SP
            M=D
            """.format(self.config.stack_base)))

    def cg_stop(self):
        self.asm(unindent("""
            (__STOP)
            @__STOP
            0;JEQ
            """))


if __name__ == '__main__':
    import os
    import sys

    fn = sys.argv[1]
    ns = os.path.split(fn)[-1].split('.')[0]

    with open(fn, 'r') as src:
        print(CodeWriter(src.read(), ns).genCode())

