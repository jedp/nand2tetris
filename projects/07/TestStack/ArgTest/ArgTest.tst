load ArgTest.asm,
output-file ArgTest.out,
compare-to ArgTest.cmp,
output-list RAM[0]%D2.6.2 RAM[2]%D2.6.2
          RAM[256]%D2.6.2
          RAM[1000]%D2.6.2 RAM[1004]%D2.6.2;

set RAM[0] 256,  // initializes the stack pointer
set RAM[2] 1000, // argument segment base

repeat 200 {    // enough cycles to complete the execution
  ticktock;
}

output;
