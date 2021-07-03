load TempTest.asm,
output-file TempTest.out,
compare-to TempTest.cmp,
output-list RAM[0]%D2.6.2
          RAM[256]%D2.6.2
          RAM[5]%D2.6.2 RAM[6]%D2.6.2;

set RAM[0] 256,  // initializes the stack pointer

repeat 300 {    // enough cycles to complete the execution
  ticktock;
}

output;
