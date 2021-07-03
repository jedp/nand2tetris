## nand2tetris

Exercises for the book, "The Elements of Computing Systems", by Nisan and Schocken, MIT Press.  

Project files downloaded from www.nand2tetris.org


### Useful Things

#### Chapter 6

[HackAssembler.py](projects/06/HackAssembler.py) converts Hack asm to machine code.

Run on a filename, or use `HackAssembler.py test` to demonstrate that it
assembles the source for `Sum1ToN.asm` on page 105 of the book.

#### Chapter 7

[VM2Hack.py](projects/07/VM2Hack.py) is a front-end for the
[vm2hack](projects/07/vm2hack/) translator.  It converts Hack vm to asm.

[test.py](projects/07/test.py) finds all the vm files in the current directory,
or those specified by basename, translatest them to asm, and runs all the tests
for them.

(Should be easy to adapt to a different project by replacing the line `asm =
Translator(vm_filepath).translate()` with whatever works for you.)

![Test Output Image](test.png)

