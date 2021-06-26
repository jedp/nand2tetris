#!/usr/bin/env python3

if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), "vm2hack"))
    print(sys.path)

    from vm2hack.compiler import Compiler
    fn = sys.argv[1]
    with open(fn, 'r') as src:
        print(Compiler(src.read()).compile())

