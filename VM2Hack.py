#!/usr/bin/env python3

if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), "vm2hack"))

    from vm2hack.translator import Translator
    print(Translator(sys.argv[1]).translate())

