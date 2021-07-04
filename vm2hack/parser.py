#!/usr/bin/env python3

from collections import namedtuple

C_ERROR = 'Error'
C_ARITHMETIC = 'Arithmetic'
C_PUSH = 'Push'
C_POP = 'Pop'
C_LABEL = 'Label'
C_GOTO = 'Goto'
C_IF_GOTO = 'If-Goto'
C_FUNCTION = 'Function'
C_CALL = 'Call'
C_RETURN = 'Return'

commands = {
    'add': C_ARITHMETIC,
    'sub': C_ARITHMETIC,
    'neg': C_ARITHMETIC,
    'eq': C_ARITHMETIC,
    'gt': C_ARITHMETIC,
    'lt': C_ARITHMETIC,
    'and': C_ARITHMETIC,
    'or': C_ARITHMETIC,
    'not': C_ARITHMETIC,
    'push': C_PUSH,
    'pop': C_POP,
    'label': C_LABEL,
    'goto': C_GOTO,
    'if-goto': C_IF_GOTO,
    'function': C_FUNCTION,
    'call': C_CALL,
    'return': C_RETURN
}

segments = (
    'argument',
    'local',
    'static',
    'constant',
    'this',
    'that',
    'pointer',
    'temp'
)

# src = original source code line
# type= command type
# arg1 = arg1, or command name if arithmetic, or None
# arg2 = arg2 or None
Cmd = namedtuple('Command', 'line src type arg1 arg2')
Err = namedtuple('Command', 'line type msg')

class Parser:
    def __init__(self, text):
        self.text = text
        self.line = 0
        self.lines = self.text.splitlines()
        self.cmds = []
        self.errs = []

    def parse(self):
        for line in self.lines:
            self.parseTokens(self.tokenizeLine(line))
            self.line += 1

        return {
            'commands': self.cmds,
            'errors': self.errs
        }

    def tokenizeLine(self, line):
        # Discard comments; split into tokens.
        return line.split("//")[0].split()

    def makeCmd(self, type, arg1=None, arg2=None):
        return Cmd(self.line, self.lines[self.line], type, arg1, arg2)

    def parseTokens(self, tokens):
        if not tokens:
            return

        if len(tokens) > 3:
            self.errs.append(Err(self.line, C_ERROR, "Too many words."))
            return

        if tokens[0] not in commands:
            self.errs.append(Err(self.line, C_ERROR, "Bad command: {}".format(tokens[0])))
            return
        command = commands.get(tokens[0])

        if command == C_RETURN:
            self.cmds.append(self.makeCmd(command))
            return
        # For arithmetic commands: arg1 is the name of the command.
        if command == C_ARITHMETIC:
            self.cmds.append(self.makeCmd(command, tokens[0]))
            return

        if len(tokens) == 2:
            self.cmds.append(self.makeCmd(command, tokens[1]))
            return

        self.cmds.append(self.makeCmd(command, tokens[1], tokens[2]))

if __name__ == '__main__':
    import sys
    import pprint
    fn = sys.argv[1]

    with open(fn, 'r') as src:
        pprint.pprint(Parser(src.read()).parse())

