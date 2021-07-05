#!/usr/bin/env python3

import os
from vm2hack.writer import CodeWriter


def find_vm_files(dirpath):
    """
    Find all Hack .vm files under root_dir.

    Return list of paths to .vm files.
    """
    vm_filepaths = []
    for root, dirs, files in os.walk(dirpath):
         for f in files:
             if f.endswith(".vm"):
                vm_filepaths.append(os.path.join(dirpath, f))

    return vm_filepaths


class Translator:
    def __init__(self, dirname):
        self.dir = dirname

    def translate(self):
        inputs = {}
        for vm_filepath in find_vm_files(self.dir):
            ns = os.path.split(vm_filepath)[-1].split('.')[0]
            with open(vm_filepath, 'r') as src:
                inputs[ns] = src.read()

        return CodeWriter(inputs).genCode()

