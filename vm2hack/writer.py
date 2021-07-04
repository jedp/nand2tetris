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

    _cg_push_D =unindent("""
        @SP             // MEM[SP] = D
        A=M
        M=D
        @SP             // SP++
        M=M+1
        """)

    _cg_pop_D = unindent("""
        @SP
        AM=M-1          // SP--
        D=M             // D = MEM[SP]
        """)

    def __init__(self, vm_code, ns, config=Config()):
        self.input = Parser(vm_code).parse()
        self.config = config
        self.text = []
        self.ns = ns
        self.function_name_stack = [None]
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

        if cmd.type == 'Label':
            return self.cg_label(cmd)

        if cmd.type == 'Goto':
            return self.cg_goto(cmd)

        if cmd.type == 'If-Goto':
            return self.cg_if_goto(cmd)

        if cmd.type == 'Function':
           return self.cg_function(cmd)

        if cmd.type == 'Call':
           return self.cg_call(cmd)

        if cmd.type == 'Return':
           return self.cg_return(cmd)

        raise ValueError(f"Unhandled command: {cmd}")

    def _cg_push_addr(self, reg, comment):
        self.asm(unindent(f"""
            @{reg}          // {comment}
            D=A             // Address {reg}
            {self._cg_push_D}
            """))

    def _cg_push_mem(self, reg, comment):
        self.asm(unindent(f"""
            @{reg}          // {comment}
            D=M             // Contents of mem at addr {reg}
            {self._cg_push_D}
            """))


    def makeLabel(self, cmd):
        """
        Let foo be a function within the file Xxx.vm. The handling of each
        `label bar` command within foo generates, and injects into the assembly
        code stream, the symbol Xxx.foo$bar.

        When translating `goto bar` and `if-goto bar` commands (within foo)
        into assembly, the label Xxx.foo$bar must be used instead of bar.
        """
        if self.function_name_stack[-1] is not None:
            prefix = self.ns + '.' + self.function_name_stack[-1]
        else:
            prefix = self.ns
        return prefix + '$' + cmd.arg1

    def cg_function(self, cmd):
        """
        Marks the beginning of a function named cmd.arg1.
        The command has cmd.arg2 local variables.
        """
        self.function_name_stack.append(cmd.arg1)
        funcAddress = self.makeLabel(cmd)
        nvars = int(cmd.arg2)
        self.asm(unindent(f"""
            // Function {cmd.arg1} {cmd.arg2}
            ({funcAddress})
            """))
        for i in range(nvars):
            self._cg_push_addr(0, f"Init local{i} to 0")

    def cg_call(self, cmd):
        """
        Calls the function named in cmd.arg1.
        Indicates that cmd.arg2 args have been pushed onto the stack already.
        """
        nargs = int(cmd.arg2)
        returnAddress = self.uniqueLabel()
        funcAddress = self.makeLabel(cmd)
        self._cg_push_addr(returnAddress, "Return address")
        self._cg_push_mem("LCL", "Save caller's LCL")
        self._cg_push_mem("ARG", "Save caller's ARG")
        self._cg_push_mem("THIS", "Save caller's THIS")
        self._cg_push_mem("THAT", "Save caller's THAT")
        # Calculate ARG = SP - 5 - nargs
        self._cg_push_mem("SP", "Current SP")
        self._cg_push_addr("5", "Constant 5")
        self.asm("sub       // SP - 5")
        self._cg_push_addr(nargs, "Num Args")
        self.asm("sub       // SP - 5 - nArgs")
        self.asm(unindent(f"""
            @{self._cg_pop_D}
            @ARG
            M=D             // Reposition ARG: SP - 5 - nargs
            @SP
            D=M
            @LCL            // Reposition LCL: SP
            M=D
            @{funcAddress}
            0;JEQ
            ({returnAddress})
            """))

    def cg_return(self, cmd):
        """
        Transfers execution to the command just following the call command
        in the code of the function that called the current function.
        """
        self.function_name_stack.pop()
        temp = self.config.temp_base
        # Reposition return value for caller
        self.asm(unindent(f"""
            {self._cg_pop_D}
            @ARG
            A=M
            M=D             // *ARG = pop()
            @ARG
            D=M
            D=D+1
            @SP
            M=D             // SP = ARG + 1
            """))
        # Store LCL in temp var and work backwards to restore state.
        self.asm(unindent(f"""
            @LCL
            D=M
            @{temp}
            M=D             // temp0 = frame = LCL
            """))
        # THAT    = --temp (LCL - 1)
        # THIS    = --temp (LCL - 2)
        # ARG     = --temp (LCL - 3)
        # LCL     = --temp (LCL - 4)
        for reg in ['THAT', 'THIS', 'ARG', 'LCL']:
            self.asm(unindent(f"""
                @{temp}
                M=M-1           // temp--
                @{temp}
                A=M
                D=M
                @{reg}
                M=D             // {reg} = frame[temp]
                """))
        # retAddr = --temp (LCL - 5)
        self.asm(unindent(f"""
            @{temp}
            M=M-1           // temp--
            @{temp}
            A=M
            D=M
            0;JEQ           // Jump to return address = frame - 5
            """))

    def cg_label(self, cmd):
        """
        Labels the current location in the function's code.
        """
        label = self.makeLabel(cmd)
        self.asm(f"({label})")

    def cg_goto(self, cmd):
        """
        Effects an unconditional goto operation, causing execution to continue
        from the location marked by the label. The goto command and the labeled
        jump destination must be located in the same function.
        """
        label = self.makeLabel(cmd)
        self.asm(unindent(f"""
            @{label}
            0;JMP
            """))

    def cg_if_goto(self, cmd):
        """
        Effects a conditional goto operation. The stack's topmost value is
        popped; if the value is not zero, execution continues from the location
        marked by the label; otherwise, execution continues from the next
        command in the program. The if-goto command and the labeled jump
        destination must be located in the same function.
        """
        label = self.makeLabel(cmd)
        self.asm(unindent(f"""
            @SP
            AM=M-1      // SP --
            D=M         // D = MEM[SP]
            @{label}
            D;JNE       // if-goto {label}
            """))

    def cg_push_constant(self, cmd):
        """
        Push a constant value on the stack.

        Value must be positive, unsigned int between 0 and 32767.
        """
        assert(cmd.arg1 == 'constant')
        self._cg_push_addr(cmd.arg2, f"Constant {cmd.arg2}")

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
            {self._cg_pop_D}
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
        self._cg_push_mem(addr, f"Temp base + offset {cmd.arg2}")

    def cg_pop_temp(self, cmd):
        """
        Pop and store at offset in temp segment.
        """
        assert(cmd.arg1 == 'temp')
        addr = self.config.temp_base + int(cmd.arg2)
        self.asm(unindent(f"""
            {self._cg_pop_D}
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
        self._cg_push_mem(addr, f"Pointer {cmd.arg2} addr")

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
            {self._cg_pop_D}
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
        self._cg_push_mem(addr, f"Static addr {cmd.arg2} in {self.ns}")

    def cg_pop_static(self, cmd):
        """
        Pop the stack and store the value in the given static variable.
        """
        assert(cmd.arg1 == 'static')
        addr = self.staticAddress(cmd.arg2)
        self.asm(unindent(f"""
            {self._cg_pop_D}
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
            {self._cg_pop_D}
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
            {self._cg_push_D}
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
            {self._cg_push_D}
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
            {self._cg_pop_D}
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
            //D=A
            //@SP
            //M=D
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

