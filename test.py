#!/usr/bin/env python3
"""
Find and translate all .vm files to .asm, then run all tests without the UI.
Report results.

Usage:

Test a single thing: ./test.py PointerTest

Test all the things: ./test.py

Original script by Jed Parsons, https://github.com/jedp/nand2tetris
"""

import os
import sys
import subprocess
sys.path.append(os.path.join(os.path.dirname(__file__), "vm2hack"))
from vm2hack.translator import Translator

C_GREEN = '\033[92m'
C_RED = '\033[91m'
C_RESET = '\033[0m'


def basename(filepath):
    return os.path.splitext(os.path.split(filepath)[1])[0]


def find_vm_directories(root_dir):
    """
    Find all directories under root_dir that contain .vm files.

    Return list of paths to directories.
    """
    vm_dirs = set()
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if f.endswith(".vm"):
                vm_dirs.add(root)

    return vm_dirs


def vm2asm(vm_directory):
    """
    Translate Hack vm files to asm, overwriting any existing file.

    Return path to new .asm file.
    """
    basename = os.path.split(vm_directory)[1]
    if not basename:
        raise ValueError(f"Screwed up getting path info from: {vm_directory}")
    asm_filepath = os.path.join(vm_directory, basename+'.asm')

    asm = Translator(vm_directory).translate()
    with open(asm_filepath, 'w') as out:
        out.write(asm)
    # print(f"Translated: {vm_filepath} -> {asm_filepath}", file=sys.stderr)
    return asm_filepath


def test(asm_filepath, emulator_path):
    """
    Execute the java CPUEmulatorMain on the given Hack .tst file.

    This evaluates the test input using the .asm program in the same dir.

    Prints output on success or failure.
    """
    basepath, asm_filename = os.path.split(asm_filepath)
    basename = os.path.splitext(asm_filename)[0]
    tst_filepath = os.path.join(basepath, basename+'.tst')
    if not os.path.exists(tst_filepath):
        print(f"Test file not found: {tst_filepath}")
        return

    tools_root = os.path.split(emulator_path)[0]
    # From the CPUEmulator.sh script.
    classpath = ':'.join(
            [os.path.abspath(os.path.join(tools_root, f)) for f in [
                'bin/classes',
                'bin/lib/Hack.jar',
                'bin/lib/HackGUI.jar',
                'bin/lib/Simulators.jar',
                'bin/lib/SimulatorsGUI.jar',
                'bin/lib/Compilers.jar'
            ]])

    java_entry = 'CPUEmulatorMain'
    java_args = tst_filepath

    cmd = [
        'java',
        '-cp', '${CLASSPATH}:'+classpath,
        java_entry,
        java_args]

    p = subprocess.run(args=cmd, shell=False, capture_output=True, encoding='utf-8')
    if p.returncode != 0:
        print(f"{C_RED}Failed{C_RESET} {basepath}: {p.stderr.strip()}")
        print("Expected:")
        with open(os.path.join(basepath, basename+'.cmp')) as expected:
            print(expected.read())
        print("Got:")
        with open(os.path.join(basepath, basename+'.out')) as result:
            print(result.read())
    else:
        print(f"{C_GREEN}Passed{C_RESET} {basepath}")


if __name__ == '__main__':
    """
    Usage:

        ./test.py           Find and run all tests
        ./test.py 07        Test only things with 07 in their path
        ./test.py TestEq    Run test with basename TestEq
    """
    import re
    emulator_path = os.path.join("tools", "CPUEmulator.sh")

    match_list = sys.argv[1:]
    if (match_list):
        print("Testing: " + ", ".join(match_list))
    else:
        print("Testing everyting")

    for vm_dir in find_vm_directories("projects"):
        if match_list:
            matches = False
            for part in re.split(r'\W', vm_dir):
                if part in match_list:
                    matches = True
                    break
            if not matches:
                continue

        try:
            asm_filepath = vm2asm(vm_dir)
            test(asm_filepath, emulator_path)
        except ValueError as err:
            print(f"{C_RED}Error{C_RESET}  {vm_filepath}")
            print(err)

