#!/usr/bin/env python3

import string
import sys
from collections import namedtuple

# Immutable data classes for storing abstract representations.
Tag = namedtuple('Tag', 'line tag value', module=__name__+'.Tag')
Sym = namedtuple('Sym', 'line value labels', module=__name__+'.Sym')
Inst = namedtuple('Inst', 'line dest comp jmp labels', module=__name__+'.Inst')
Err = namedtuple('Err', 'line msg', module=__name__+'.Err')

def isType(t, T):
    """
    Python madness.
    """
    return getattr(t, "__module__", None) == __name__+'.'+T.__name__

def isSymbolChar(ch):
    """
    Return True if ch is a valid char for a symbol name.
    """
    return (ch in string.ascii_letters or
            ch in string.digits or
            ch in ['_', '.', '$', ':'])

def isMnemChar(ch):
    """
    Return True if ch is a valid char for a mnemonic.
    """
    if isSymbolChar(ch):
        return True
    return ch in ['+', '-', '|', '&', '!']

class Lexer:
    """
    Converts the input text into a stream of tokens.

    The last token emitted will be EOF.

    Call advance() to get each next token.

    Usage:

        lexer = Lexer(text)
        while lexer.token.tag != 'EOF':
            lexer.advance()
            # Do something with lexer.token
    """

    def __init__(self, text):
        self.pos = 0
        self.line = 0
        self.text = text
        self.at_eof = False
        self.token = self.makeTag('START')

    def advance(self):
        """
        Advance the lexer and return the current token.
        """
        if self.token.tag != 'EOF':
            self.token = self.get_token()
        return self.token

    # The rest of these methods are private.
    # I can't stand the leading underscore notation.
    # Just don't call them, please.

    def makeTag(self, tag, value=None):
        return Tag(self.line, tag, value)

    def readch(self):
        if self.pos >= len(self.text):
            self.at_eof = True
            return ''

        self.nextch = self.text[self.pos]
        self.pos += 1

    def unreadch(self):
        self.pos -= 1
        self.nextch = self.text[self.pos]

    def consume_ws(self):
        while(True):
            self.readch()

            if self.nextch not in [' ', '\t', '\r']:
                return

    def consume_all(self):
        while(True):
            self.readch()

            if self.nextch == '\n':
                return
            if self.at_eof:
                return

    def eat(self, ch):
        self.readch()
        return self.nextch == ch

    def lex_word(self):
        word = "" + self.nextch
        self.readch()
        while isSymbolChar(self.nextch):
            word += self.nextch
            self.readch()
        self.unreadch()
        return word

    def lex_mnem(self):
        mnem = "" + self.nextch
        self.readch()
        while isMnemChar(self.nextch):
            mnem += self.nextch
            self.readch()
        self.unreadch()
        return self.makeTag('MNEM', mnem)

    def lex_newline(self):
        if not self.eat('\n'):
            return self.makeTag('ERROR', 'End of line was expected')

        newline = self.makeTag('NEWLINE')
        self.line += 1
        return newline

    def lex_label(self):
        self.eat('(')
        label = self.lex_word()
        self.eat(')')
        return self.makeTag('LABEL', label)

    def get_token(self):
        self.consume_ws()
        if self.at_eof:
            return self.makeTag('EOF')

        ch = self.nextch

        # Mnemonic
        if isMnemChar(ch):
            return self.lex_mnem()
        # Label
        if ch == '(':
            label = self.lex_label()
            self.readch()
            return label
        # Comment
        if ch == '/':
            self.consume_all()
            self.unreadch()
            return self.lex_newline()
        # Assignment
        if ch == '=':
            return self.makeTag('ASSIGN')
        # Optional jump separator
        if ch == ';':
            return self.makeTag('SEMICOLON')
        # Constant sentinel
        if ch == '@':
            return self.makeTag('AT_SIGN')
        # End of line
        if ch == '\n':
            self.unreadch()
            return self.lex_newline()

        return self.makeTag('UNKNOWN', ch)


class ParserState:
    """
    Mutable data class for use in parser state machine.
    """
    def __init__(self):
        self.sym = None
        self.dest = None
        self.comp = None
        self.jmp = None
        self.labels = []
        self.expect_sym = False
        self.expect_jmp = False

class Parser:
    """
    Parse lexer output and create an abstract syntax representation.

    The abstract representation is a list of either Sym, Inst, or Err tuples.

    Pretend the T in AST stands for Tuples :)

    Usage:
        parser = Parser(text)
        ast = parser.parse()
    """

    def __init__(self, text):
        self.lexer = Lexer(text)
        self.ast = []
        self.line = 0

    def parse(self):
        state = ParserState()

        while self.lexer.token.tag != 'EOF':
            self.lexer.advance()
            token = self.lexer.token

            if token.tag == 'AT_SIGN':
                state.expect_sym = True

            elif token.tag == 'MNEM':
                if state.expect_sym:
                    state.sym = token.value
                elif state.expect_jmp:
                    state.jmp = token.value
                else:
                    state.comp = token.value

            elif token.tag == 'ASSIGN':
                state.dest = state.comp
                state.comp = None

            elif token.tag == 'SEMICOLON':
                state.expect_jmp = True

            elif token.tag == 'LABEL':
                state.labels.append(token.value)

            elif token.tag == 'NEWLINE':
                if state.sym:
                    self.ast.append(
                            Sym(
                                self.line,
                                state.sym,
                                state.labels))
                    state = ParserState()
                    self.line += 1
                elif state.comp:
                    self.ast.append(
                            Inst(
                                self.line,
                                state.dest,
                                state.comp,
                                state.jmp,
                                state.labels))
                    state = ParserState()
                    self.line += 1

            elif token.tag == 'EOF':
                pass

            else:
                self.ast.append(Err(self.line, token.tag))
                state = ParserState()

        return self.ast


class Assembler:
    """
    Convert asm to binary string.

    On error, prints errors summaries and returns empty string.

    Usage:
        assembler = Assembler(asm)
        binary = assembler.assemble()
    """

    COMP = {
        #       acccccc
        '0':   '0101010',
        '1':   '0111111',
        '-1':  '0111010',
        'D':   '0001100',
        'A':   '0110000',
        'M':   '1110000',
        '!D':  '0001101',
        '!A':  '0110001',
        '!M':  '1110001',
        '-D':  '0001111',
        '-A':  '0110011',
        '-M':  '1110011',
        'D+1': '0011111',
        'A+1': '0110111',
        'M+1': '1110111',
        'D-1': '0001110',
        'A-1': '0110010',
        'M-1': '1110010',
        'D+A': '0000010', 'A+D': '0000010',
        'D+M': '1000010', 'M+D': '1000010',
        'D-A': '0010011',
        'D-M': '1010011',
        'A-D': '0000111',
        'M-D': '1000111',
        'D&A': '0000000', 'A&D': '0000000',
        'D&M': '1000000', 'M&D': '1000000',
        'D|A': '0010101', 'A|D': '0010101',
        'D|M': '1010101', 'M|D': '1010101'
    }

    DEST = {
        None:  '000',
        'M':   '001',
        'D':   '010',
        'DM':  '011', 'MD':  '011',
        'A':   '100',
        'AM':  '101', 'MA':  '101',
        'AD':  '110', 'DA':  '110',
        'ADM': '111', 'AMD': '111', 'MAD': '111', 'MDA': '111', 'DAM': '111', 'DMA': '111'
    }

    JMP = {
        None:  '000',
        'JGT': '001',
        'JEQ': '010',
        'JGE': '011',
        'JLT': '100',
        'JNE': '101',
        'JLE': '110',
        'JMP': '111'
    }

    def __init__(self, text):
        self.sym = {
            'R0':         0,
            'R1':         1,
            'R2':         2,
            'R3':         3,
            'R4':         4,
            'R5':         5,
            'R6':         6,
            'R7':         7,
            'R8':         8,
            'R9':         9,
            'R10':       10,
            'R11':       11,
            'R12':       12,
            'R13':       13,
            'R14':       14,
            'R15':       15,
            'SP':         0,
            'LCL':        1,
            'ARG':        2,
            'THIS':       3,
            'THAT':       4,
            'SCREEN': 16384,
            'KBD':    24576
        }
        self.parser = Parser(text)
        self.errors = []
        self.code = []
        self.nextvar = 16

    def resolveSymbols(self, ast):
        for line in ast:
            # Labels
            if isType(line, Inst) or isType(line, Sym):
                for label in line.labels:
                    if label in self.sym:
                        self.errors.append(f'Cannot redefine {label} at {line.line}')
                    else:
                        self.sym[label] = line.line

    def generateCode(self, ast):
        for line in ast:
            # A-Instruction
            if isType(line, Sym) and line.value.isnumeric():
                self.code.append(format(int(line.value), '016b'))


            # Automatic variable.
            elif isType(line, Sym) and line.value not in self.sym:
                self.sym[line.value] = self.nextvar
                self.nextvar += 1
                if self.nextvar == self.sym['SCREEN']:
                    raise ValueError("Insufficient memory to store {line.value}")

                else:
                    if line.value not in self.sym:
                        self.errors.append(
                                'Variable {} not found at {}'.format(
                                    line.value, line.line))
                    else:
                        value = self.sym[line.value]
                        self.code.append(format(int(value), '016b'))

            # Reference to label.
            elif isType(line, Sym):
                self.code.append(format(self.sym[line.value], '016b'))

            elif isType(line, Inst):
                try:
                    prefix = '111'
                    comp = self.COMP[line.comp]
                    dest = self.DEST[line.dest]
                    jmp = self.JMP[line.jmp]
                    self.code.append(prefix + comp + dest + jmp)
                except KeyError as e:
                    if line.comp not in self.COMP:
                        self.errors.append(f'Unknown comp "{line.comp}" at {line.line}')
                    elif line.dest not in self.DEST:
                        self.errors.append(f'Unknown dest "{line.dest}" at {line.line}')
                    elif line.jmp not in self.JMP:
                        self.errors.append(f'Unknown jmp "{line.jmp}" at {line.line}')
                    else:
                        raise e

            elif isType(line, Err):
                self.errors.append(line.msg)

    def assemble(self):
        ast = self.parser.parse()
        self.resolveSymbols(ast)
        self.generateCode(ast)
        if self.errors:
            for err in self.errors:
                print(err, file=sys.stderr)
            return ""
        return '\n'.join(self.code)


def assembleFile(filename):
    with open(filename, 'r') as src:
        return Assembler(src.read()).assemble()


test_asm="""\
// Computes R1=1 + ... + R0
    // i = 1
    @i
    M=1
    // sum = 0
    @sum
    M=0
 (LOOP)
    // If i > R0 goto STOP
    @i
    D=M
    @R0
    D=D-M
    @STOP
    D;JGT
    // sum += i
    @i
    D=M
    @sum
    M=D+M
    // i++
    @i
    M=M+1
    @LOOP
    0;JMP
 (STOP)
    @STOP
    0;JMP
"""

test_bin = """\
0000000000010000
1110111111001000
0000000000010001
1110101010001000
0000000000010000
1111110000010000
0000000000000000
1111010011010000
0000000000010010
1110001100000001
0000000000010000
1111110000010000
0000000000010001
1111000010001000
0000000000010000
1111110111001000
0000000000000100
1110101010000111
0000000000010010
1110101010000111\
"""

def test():
    assembler = Assembler(test_asm)
    output = assembler.assemble()

    if output:
        if output == test_bin:
            print("Success. Results as expected.")
            print(output)
        else:
            print("Results differ from expected.")

            result = output.split('\n')
            expected = test_bin.split('\n')
            for line in range(len(expected)):
                if line < len(result):
                    if result[line] != expected[line]:
                        print("Line {}: Expected {}; got: {}".format(
                            line, expected[line], result[line]))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Filename required", file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] == 'test':
        test()

    else:
        print(assembleFile(sys.argv[1]))

