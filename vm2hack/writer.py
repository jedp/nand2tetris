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

    _cg_push_D = unindent("""
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

    def __init__(self, inputs, config=Config()):
        self.inputs = inputs
        self.ns = None
        self.config = config
        self.text = []
        self.function_name_stack = [None]
        self.next_static = 0
        self.next_label = 0
        self.static_offsets = {}

    def genCode(self):
        """
        Generate the complete asm output.
        """
        # Init variables and environment.
        if 'Sys' in self.inputs:
            self.cg_bootstrap_sys()

        for ns, vm_code in self.inputs.items():
            input = Parser(vm_code).parse()
            self.ns = ns

            if input['errors']:
                # No meaningful output can be generated.
                # Print errors to stderr and return empty string.
                print("ERRORS", file=sys.stderr)
                for err in input['errors']:
                    print("Line {}: {}".format(err.line, err.msg))
                return f"// Encountered errors parsing {filename}"

            # Translate input.
            self.asm(f"// *** Parsing input file '{ns}' ***")
            for cmd in input['commands']:
                # Print original VM command as a comment.
                self.asm('// ' + cmd.src)
                self.cg(cmd)
            self.asm(f"// *** End of input file '{ns}' ***")

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
        label = f"$L{self.next_label}"
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

    def _cg_push_value(self, uint, comment):
        self.asm(unindent(f"""
            @{uint}         // {comment}
            D=A             // D = {uint}
            {self._cg_push_D}
            """))

    def _cg_push_mem(self, reg, comment):
        self.asm(unindent(f"""
            @{reg}          // {comment}
            D=M             // D = *({reg})
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
        if cmd.type in ['Function', 'Call']:
            return self.ns + ':' + cmd.arg1

        if self.function_name_stack[-1] is not None:
            prefix = self.ns + ':' + self.function_name_stack[-1]
        else:
            prefix = self.ns
        return prefix + '$' + cmd.arg1

    def cg_bootstrap_sys(self):
        """
        Initialize SP to 256 and call Sys.init.
        """
        self.asm(unindent("""
            @256
            D=A
            @SP
            M=D                 // SP = 256
            """))
        self.asm("// Call Sys.init")
        self._cg_function_call('Sys:Sys.init', 'STOP', '0')

    def cg_function(self, cmd):
        """
        Marks the beginning of a function named cmd.arg1.
        The command has cmd.arg2 local variables.
        """
        self.function_name_stack.append(cmd.arg1)
        funcAddress = self.makeLabel(cmd)
        nvars = int(cmd.arg2)
        self.asm(unindent(f"""
            ({funcAddress})         // Label for func {cmd.arg1}
            """))
        for i in range(nvars):
            self.asm(unindent(f"""
                @0                  // Init arg{i} = 0
                D=A
                {self._cg_push_D}
                """))

    def _cg_function_call(self, funcAddress, returnAddress, nargs):
        """
        Calls the function named in cmd.arg1.
        Indicates that cmd.arg2 args have been pushed onto the stack already.
        """
        self._cg_push_value(returnAddress, "Return address")
        for reg in ['LCL', 'ARG', 'THIS', 'THAT']:
            self._cg_push_mem(reg, f"Save caller's {reg}")
        # Calculate ARG = SP - nargs - 5
        self.asm(unindent(f"""
            //@SP
            D=M             // D = SP
            @{nargs}
            D=D-A           // D = SP - nargs
            @5
            D=D-A           // D = SP - nargs - 5
            @ARG
            M=D             // Reposition ARG: ARG = SP - nargs - 5
            @SP
            D=M
            @LCL            // Reposition LCL: LCL = SP
            M=D
            @{funcAddress}
            0;JMP
            ({returnAddress})
            """))

    def cg_call(self, cmd):
        funcAddress = self.makeLabel(cmd)
        returnAddress = self.uniqueLabel()
        nargs = int(cmd.arg2)
        self._cg_function_call(funcAddress, returnAddress, nargs)

    def cg_return(self, cmd):
        """
        Transfers execution to the command just following the call command
        in the code of the function that called the current function.
        """
        self.function_name_stack.pop()
        self.asm(unindent(f"""
            // Save frame in R13
            @LCL            // Frame = LCL
            D=M
            @R13
            M=D             // R13 = frame = LCL
            // Save return address in R14
            @5
            D=D-A
            A=D
            D=M             // D = *(frame - 5)
            @R14
            M=D             // R14 = return address = *(frame - 5)
            // *ARG = pop()
            {self._cg_pop_D}
            @ARG
            A=M
            M=D             // *ARG = pop()
            // SP = ARG + 1
            @ARG
            D=M+1
            @SP
            M=D             // SP = ARG + 1
            """))
        # THAT    = *(frame - 1)
        # THIS    = *(frame - 2)
        # ARG     = *(frame - 3)
        # LCL     = *(frame - 4)
        for i, reg in enumerate(['THAT', 'THIS', 'ARG', 'LCL']):
            i = i + 1
            self.asm(unindent(f"""
                @R13
                D=M
                @{i}
                D=D-A
                A=D
                D=M
                @{reg}          // {reg} = *(frame - {i})
                M=D
                """))
        self.asm(unindent(f"""
            @R14
            A=M
            0;JMP           // Jump to return address = *(frame - 5)
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
        self._cg_push_value(cmd.arg2, f"Constant {cmd.arg2}")

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
            A=D+A           // A = addr of {cmd.arg1} {cmd.arg2}
            D=M             // D = *(addr)
            {self._cg_push_D}
            """))

    def cg_pop_segment(self, cmd):
        """
        Pop and store in segment+offset.
        """
        assert(cmd.arg1 in self.config.segments)
        base_ptr = self.config.segments[cmd.arg1]
        offset = int(cmd.arg2)
        self.asm(unindent(f"""
            // Pop addr {base_ptr} + {cmd.arg2}
            @{base_ptr}     // Base segment {cmd.arg1}
            D=M
            @{offset}       // Offset {cmd.arg2}
            D=D+A           // base + offset
            @R13
            M=D             // R13 = base + offset
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
        reg = f"{addr}"
        self._cg_push_mem(reg, f"Temp base + offset {cmd.arg2}")

    def cg_pop_temp(self, cmd):
        """
        Pop and store at offset in temp segment.
        """
        assert(cmd.arg1 == 'temp')
        addr = self.config.temp_base + int(cmd.arg2)
        self.asm(unindent(f"""
            {self._cg_pop_D}
            @R{addr}        // Temp base + offset {cmd.arg2}
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
        reg = f"{addr}"
        self._cg_push_mem(reg, f"Pointer {cmd.arg2} addr")

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
            @R{addr}        // Pointer {cmd.arg2} addr
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
            @{addr}
            D=M
            {self._cg_push_D}
            """))

    def cg_pop_static(self, cmd):
        """
        Pop the stack and store the value in the given static variable.
        """
        assert(cmd.arg1 == 'static')
        addr = self.staticAddress(cmd.arg2)
        self.asm(unindent(f"""
            {self._cg_pop_D}
            @{addr}         // Static {self.ns}.{cmd.arg2} = {addr}
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
            0;JMP
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

    def cg_stop(self):
        label = self.uniqueLabel()
        self.asm(unindent(f"""
            (STOP)
            @STOP
            0;JMP
            """))


if __name__ == '__main__':
    import os
    import sys

    fn = sys.argv[1]
    ns = os.path.split(fn)[-1].split('.')[0]

    with open(fn, 'r') as src:
        print(CodeWriter(src.read(), ns).genCode())

