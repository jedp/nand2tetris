#!/usr/bin/env python3

from enum import Enum
from collections import namedtuple

C_ERROR = 'Error'
C_ARITHMETIC = 'Arithmetic'
C_PUSH = 'Push'
C_POP = 'Pop'

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
    'pop': C_POP
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

Cmd = namedtuple('Command', 'line type arg1 arg2')
Err = namedtuple('Command', 'line type msg')

class Parser:
    def __init__(self, text):
        self.text = text
        self.line = 0
        self.cmds = []
        self.errs = []

    def parse(self):
        for line in self.text.splitlines():
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
        return Cmd(self.line, type, arg1, arg2)

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
        # For arithmetic commands: arg1 is the name of the command.
        if command == C_ARITHMETIC:
            self.cmds.append(self.makeCmd(command, tokens[0]))
            return

        if len(tokens) != 3:
            self.errs.append(Err(self.line, C_ERROR, "Too few args for {}".format(tokens[0])))
            return

        self.cmds.append(self.makeCmd(command, tokens[1], tokens[2]))

if __name__ == '__main__':
    import sys
    import pprint
    fn = sys.argv[1]

    with open(fn, 'r') as src:
        pprint.pprint(Parser(src.read()).parse())

