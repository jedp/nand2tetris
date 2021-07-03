load TestGt.asm,
output-file TestGt.out,
compare-to TestGt.cmp,
output-list RAM[0]%D2.6.2 
        RAM[256]%D2.6.2 RAM[257]%D2.6.2 RAM[258]%D2.6.2;

set RAM[0] 256,  // initializes the stack pointer

repeat 400 {     // enough cycles to complete the execution
  ticktock;
}

output;
