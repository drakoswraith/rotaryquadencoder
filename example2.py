# https://github.com/drakoswraith/rotaryquadencoder
# Use the rotaryQuadEncoder with it's internal count tracking via interrupts

import micropython
micropython.alloc_emergency_exception_buf(100)

from machine import Pin
import time
from rotary_quad_encoder import RotaryQuadEncoder

r = RotaryQuadEncoder(pin1=12, pin2=13, half_steps=True, pins_pull_up=False,
    track_count=True, reverse=False, range_mode=RotaryQuadEncoder.RANGE_WRAP, min=0, max=1024) 
             
def rotate(pin):
    global r
    result = r.process()
    if result != None:
        print(result)
    
r.pin1.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=rotate)
r.pin2.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=rotate)
r.process()

while True:
    time.sleep_ms(50)
    