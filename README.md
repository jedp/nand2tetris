## nand2tetris

Exercises for the book, "The Elements of Computing Systems", by Nisan and Schocken, MIT Press.  

Project files downloaded from www.nand2tetris.org


### Useful Things

#### Chapter 6

[HackAssembler.py](projects/06/HackAssembler.py) converts Hack asm to machine code.

Run on a filename, or use `HackAssembler.py test` to demonstrate that it
assembles the source for `Sum1ToN.asm` on page 105 of the book.

#### Chapters 7 and 8

[VM2Hack.py](VM2Hack.py) is a front-end for the
[vm2hack](vm2hack/) translator.  It converts Hack vm to asm.

[test.py](test.py) finds all the vm files under the `projects` directory,
translates them to asm, and runs the tests that accompany them.

Usage:
- `./test.py` to translate all vm files run all tests in all projects.
- `./test.py 07` to translate vm files and run all tests in project `07`.
- `./test.py TestEq` to find and translate `TestEq.vm` and run `TestEq.tst`.

(Should be easy to adapt to a different project by replacing the line `asm =
Translator(vm_filepath).translate()` with whatever works for you.)

![Test Output Image](test.png)

