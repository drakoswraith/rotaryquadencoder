# RotaryQuadEncoder
Micropython library for using rotary quadrature encoders, such as the KY-040
https://github.com/drakoswraith/rotaryquadencoder


# Sources
This is essentially a straight port of Buxtronix's rotary library with the addition of Mike Teachman's counting functions
http://www.buxtronix.net/2011/10/rotary-encoders-done-properly.html
https://github.com/buxtronix/arduino/tree/master/libraries/Rotary

I used the counting functions from:
https://github.com/MikeTeachman/micropython-rotary

I did not use/improve Teachman's port due to not implementing half steps, and not handling the missed first count - the encoder must be have a full pulse sent before it starts counting. I added the call to self.process below to take care of that.
I had difficulty attempting to mach up the tables between the two sets of code to address these issues, and i found it simpler to port Buxtronix's code directly for consistency between c++ and micropython. So, appologies to Mike for not contributing back to his project!


# Rotary Info:
See http://eeshop.unl.edu/pdf/KEYES%20Rotary%20encoder%20module%20KY-040.pdf#page=3&zoom=auto,-87,659


# Examples
example.py shows the basic use of interrupts and getting the raw result back that you can then check for a CW or CCW movement

example2.py shows letting this class handle tracking the overall count, and what is returned is the current total count value (or None if the event was not a valid increment)

I didn't create a polling example.  Refer to Buxtronix's examples to see the basic method to do that


# Return Values
If track_count is false, the 'process' is the state machine value for the next state.  If that value equals the DIR_CW or DIR_CCW states, then a increment event has occured.
Any other value can be ignored

If track_count is true, when you create the RotaryQuadEncoder object, then the object will increment or decrement a counter value and return the current value.
If the process function is called for any invalid events, then None is returned rather than the actual counter value. You can thus test for None to know whether to respond to the event or not.

If you are tracking the count, it will work with one of three modes:
* Unbounded = Value will count up or down forever
* Bounded = Value will not go outside the min/max values, even if the physical encoder keeps going
* Wrap = Value will wrap around from the minimum to maximum value and vice versa


# Buxtronix's Original Notes (how it works)
Please See Buxtronix's site for any updates, etc....



 A typical mechanical rotary encoder emits a two bit gray code
 on 3 output pins. Every step in the output (often accompanied
 by a physical 'click') generates a specific sequence of output
 codes on the pins.

 There are 3 pins used for the rotary encoding - one common and
 two 'bit' pins.

 The following is the typical sequence of code on the output when
 moving from one step to the next:

   Position   Bit1   Bit2
   ----------------------
     Step1     0      0
      1/4      1      0
      1/2      1      1
      3/4      0      1
     Step2     0      0

 From this table, we can see that when moving from one 'click' to
 the next, there are 4 changes in the output code.

 - From an initial 0 - 0, Bit1 goes high, Bit0 stays low.
 - Then both bits are high, halfway through the step.
 - Then Bit1 goes low, but Bit2 stays high.
 - Finally at the end of the step, both bits return to 0.

 Detecting the direction is easy - the table simply goes in the other
 direction (read up instead of down).

 To decode this, we use a simple state machine. Every time the output
 code changes, it follows state, until finally a full steps worth of
 code is received (in the correct order). At the final 0-0, it returns
 a value indicating a step in one direction or the other.

 It's also possible to use 'half-step' mode. This just emits an event
 at both the 0-0 and 1-1 positions. This might be useful for some
 encoders where you want to detect all positions.

 If an invalid state happens (for example we go from '0-1' straight
 to '1-0'), the state machine resets to the start until 0-0 and the
 next valid codes occur.

 The biggest advantage of using a state machine over other algorithms
 is that this has inherent debounce built in. Other algorithms emit spurious
 output with switch bounce, but this one will simply flip between
 sub-states until the bounce settles, then continue along the state
 machine.
 A side effect of debounce is that fast rotations can cause steps to
 be skipped. By not requiring debounce, fast rotations can be accurately
 measured.
 Another advantage is the ability to properly handle bad state, such
 as due to EMI, etc.
 It is also a lot simpler than others - a static state table and less
 than 10 lines of logic.
