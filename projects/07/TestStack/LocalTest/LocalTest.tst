load LocalTest.asm,
output-file LocalTest.out,
compare-to LocalTest.cmp,
output-list RAM[0]%D2.6.2 RAM[1]%D2.6.2
          RAM[256]%D2.6.2
          RAM[500]%D2.6.2 RAM[505]%D2.6.2;

set RAM[0] 256,  // initializes the stack pointer
set RAM[1] 500,  // local segment base

repeat 300 {    // enough cycles to complete the execution
  ticktock;
}

output;
