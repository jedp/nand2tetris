#!/usr/bin/env python3

import os
from vm2hack.codegen import CodeWriter

class Translator:
    def __init__(self, fn):
        self.fn = fn

    def translate(self):
        ns = os.path.split(self.fn)[-1].split('.')[0]

        with open(self.fn, 'r') as src:
            return CodeWriter(src.read(), ns).genCode()

