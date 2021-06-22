// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Init all vars to 0.
@0
D=A
@pattern    // 0 is white, -1 is black.
M=0
@lastkey    // 0 is up, non-zero is some key.
M=0
@temp       // Temp copy of lastkey.
M=D
@16384      // Screen start.
D=A

(LOOP)

  @POLL_KBD
  0;JMP
  // POLL_KBD flow always returns to LOOP.

// Get current keypress state.
// Set paint pattern according to keypress state.
// If keypress state changed, store it and jump to PAINT.
(POLL_KBD)
  @KBD
  D=M
  @temp
  M=D
  @lastkey
  D=D-M     // Compare latest KBD value.
  @UPDATE
  D;JNE     // If KBD changed, goto UPDATE.

  @LOOP
  0;JEQ     // Else return to main loop.

// When jumped to by POLL_KBD, D contains last KBD value.
// Store value and update screen.
(UPDATE)
  @temp
  D=M
  @lastkey
  M=D       // Store latest KBD value.

  // Paint white if KBD is 0; else fall through to paint black.
  @COLOR_WHITE
  D;JEQ

(COLOR_BLACK)
  @pattern
  M=-1
  @FILL
  0;JEQ

(COLOR_WHITE)
  @pattern
  M=0
  // Fall-through to FILL.

// Fill SCREEN[0..8191] (all pixel words) with current pattern.
(FILL)
  @8191
  D=A
  @i
  M=D       // i = 8191

(NEXT_PIXELS)
  @SCREEN
  D=A
  @i
  D=D+M
  @pxword   // pxword = kbd + i
  M=D

  @pattern
  D=M
  @pxword   // kbd[i] = pattern
  A=M
  M=D

  @i
  D=M-1
  @i
  M=D       // --i

  @NEXT_PIXELS
  D;JGE

  @LOOP     // Done.
  0;JEQ
