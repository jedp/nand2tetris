load ConstTest.asm,
output-file ConstTest.out,
compare-to ConstTest.cmp,
output-list RAM[0]%D2.6.2 RAM[256]%D2.6.2;

set RAM[0] 256,  // initializes the stack pointer

repeat 1300 {    // enough cycles to complete the execution
  ticktock;
}

output;
