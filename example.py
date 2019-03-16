# https://github.com/drakoswraith/rotaryquadencoder
# Use the rotaryQuadEncoder via interrupts, and track the count in the calling code

import micropython
micropython.alloc_emergency_exception_buf(100)

from machine import Pin
import time
from rotary_quad_encoder import RotaryQuadEncoder

#_DIR_CW = const(0x10)        # clockwise step
#_DIR_CCW = const(0x20)       # counter clockwise step

r = RotaryQuadEncoder(pin1=12, pin2=13, half_steps=True, pins_pull_up=False)          
counter = 0x0
def rotate(pin):
    global counter
    global r
    result = r.process()
    if result == 0x10:
        counter = counter + 0x1
        print(counter)
    elif result == 0x20:
        counter = counter - 0x1
        print(counter)
    
r.pin1.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=rotate)
r.pin2.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=rotate)


while True:
    time.sleep_ms(50)
    