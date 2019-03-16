# Licenced under the GNU GPL Version 3
# Copyright (c) 2019 Michael Lehman (drakoswraith@gmail.com)
# https://github.com/drakoswraith/rotaryquadencoder
#---------------------------------------------------------------------------------------------------------

from machine import Pin
from micropython import const

# Values returned by 'process'
_DIR_NONE = const(0x0)       # No complete step yet.
_DIR_CW = const(0x10)        # clockwise step
_DIR_CCW = const(0x20)       # counter clockwise step
_R_START = const(0x0)    


class RotaryQuadEncoder():
    RANGE_UNBOUNDED = const(1)  
    RANGE_WRAP = const(2)
    RANGE_BOUNDED = const(3)

    def __init__(self, pin1, pin2, pins_pull_up=False, half_steps=False, track_count=False, reverse=False, range_mode=RANGE_UNBOUNDED, min=0, max=1024):
        self._ttable = None
        self._state = 0x0
        self._pinstate = 0x0
        self._half_steps = half_steps
        
        self.track_count = track_count  # whether or not to track the count
        self.reverse = reverse          # whether or not to reverse the result - only applies to tracked count
        self.count = 0x0
        self.range_mode = range_mode    # which counting method to use
        self.min = min                  # min and max values for bounded/wrap
        self.max = max
      
        if pins_pull_up:
            self.pin1 = Pin(pin1, Pin.IN)
            self.pin2 = Pin(pin2, Pin.IN)
        else:
            self.pin1 = Pin(pin1, Pin.IN, Pin.PULL_UP)
            self.pin2 = Pin(pin2, Pin.IN, Pin.PULL_UP)


        # The below state table has, for each state (row), the new state
        # to set based on the next encoder output. From left to right in,
        # the table, the encoder outputs are 00, 01, 10, 11, and the value
        # in that position is the new state to set.
        if self._half_steps:
            _R_CCW_BEGIN    = 0x1
            _R_CW_BEGIN     = 0x2
            _R_START_M      = 0x3
            _R_CW_BEGIN_M   = 0x4
            _R_CCW_BEGIN_M  = 0x5
            self._ttable = (
                (_R_START_M,            _R_CW_BEGIN,     _R_CCW_BEGIN,  _R_START),              # R_START (00)
                (_R_START_M | _DIR_CCW, _R_START,        _R_CCW_BEGIN,  _R_START),              # R_CCW_BEGIN
                (_R_START_M | _DIR_CW,  _R_CW_BEGIN,     _R_START,      _R_START),              # R_CW_BEGIN
                (_R_START_M,            _R_CCW_BEGIN_M,  _R_CW_BEGIN_M, _R_START),              # R_START_M (11)
                (_R_START_M,            _R_START_M,      _R_CW_BEGIN_M, _R_START | _DIR_CW),     # R_CW_BEGIN_M
                (_R_START_M,            _R_CCW_BEGIN_M,  _R_START_M,    _R_START | _DIR_CCW),    #R_CCW_BEGIN_M
            )
        else:
            _R_CW_FINAL     = 0x1
            _R_CW_BEGIN     = 0x2
            _R_CW_NEXT      = 0x3
            _R_CCW_BEGIN    = 0x4
            _R_CCW_FINAL    = 0x5
            _R_CCW_NEXT     = 0x6
            self._ttable = (
                (_R_START,    _R_CW_BEGIN,  _R_CCW_BEGIN, _R_START),                #_R_START
                (_R_CW_NEXT,  _R_START,     _R_CW_FINAL,  _R_START | _DIR_CW),      #_R_CW_FINAL
                (_R_CW_NEXT,  _R_CW_BEGIN,  _R_START,     _R_START),                #_R_CW_BEGIN
                (_R_CW_NEXT,  _R_CW_BEGIN,  _R_CW_FINAL,  _R_START),                #_R_CW_NEXT
                (_R_CCW_NEXT, _R_START,     _R_CCW_BEGIN, _R_START),                #_R_CCW_BEGIN
                (_R_CCW_NEXT, _R_CCW_FINAL, _R_START,     _R_START | _DIR_CCW),     #_R_CCW_FINAL
                (_R_CCW_NEXT, _R_CCW_FINAL, _R_CCW_BEGIN, _R_START),                # _R_CCW_NEXT
            )
        self.process() #call once to initialize, else it will take two clicks to start counting

    def process(self):
        # Grab state of input pins.
        self._pinstate = (self.pin2.value() << 1) | self.pin1.value()
        # Determine new state from the pins and state table.
        self._state = self._ttable[self._state & 0xf][self._pinstate]
        # Return emit bits, ie the generated event.
        result = self._state & 0x30

        if self.track_count:
            increment = 0x0
            if result == 0x10:
                increment = 0x1
            elif result == 0x20:
                increment = -0x1
            
            if increment != 0x0:
                if self.reverse:
                    increment *= -1
                    
                if self.range_mode == self.RANGE_WRAP:
                    self.count = self._wrap(self.count, increment, self.min, self.max)
                elif self.range_mode == self.RANGE_BOUNDED:
                    self.count = self._bound(self.count, increment, self.min, self.max)
                else:
                    self.count += increment
                return self.count
            else: 
                return None
        else:
            return result
        
    def _wrap(self, value, incr, lower_bound, upper_bound):
        range = upper_bound - lower_bound + 1
        value = value + incr    
        
        if value < lower_bound:
            value += range * ((lower_bound - value) // range + 1)
        
        return lower_bound + (value - lower_bound) % range     

    def _bound(self, value, incr, lower_bound, upper_bound):
        return min(upper_bound, max(lower_bound, value + incr))

