load ThisThatTest.asm,
output-file ThisThatTest.out,
compare-to ThisThatTest.cmp,
output-list RAM[256]%D1.6.1 RAM[3]%D1.6.1 
            RAM[4]%D1.6.1 RAM[3032]%D1.6.1 RAM[3046]%D1.6.1;

set RAM[0] 256,   // initializes the stack pointer
set RAM[3] 3030,  // initializes the this pointer
set RAM[4] 3040,  // initializes the that pointer

repeat 450 {      // enough cycles to complete the execution
  ticktock;
}

output;
