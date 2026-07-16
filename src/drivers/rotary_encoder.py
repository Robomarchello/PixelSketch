# My rotary encoder implementation for RPI pico:)
from machine import Pin

# 11 <-> 01 <-> 00 <-> 10 <-> 11
class states:
    UNDEFINED = 0
    START = 1
    CW_A = 2
    CW_AB = 3
    CW_B = 4
    CCW_B = 5
    CCW_AB = 6
    CCW_A = 7

TRANSITION_MATRIX = [
    # 00, 01, 10, 11
    [states.UNDEFINED, states.UNDEFINED, states.UNDEFINED, states.START], # undefined
    [states.START, states.CW_A, states.CCW_B, states.START], # START transitions
    [states.CW_AB, states.CW_A, states.UNDEFINED, states.START], # clockwise a transitions (01) -> 00, 11
    [states.CW_AB, states.CW_A, states.CW_B, states.UNDEFINED], # clockwise ab transitions (00) -> 01, 10
    [states.CW_AB, states.UNDEFINED, states.CW_B, states.START], # clockwise b transitions (10) -> 00, 11
    [states.CCW_AB, states.UNDEFINED, states.CCW_B, states.START], # counterclockwise B transitions (10) -> 00, 11
    [states.CCW_AB, states.CCW_A, states.CCW_B, states.UNDEFINED], # counterclockwise ab transitions (00) -> 01, 10
    [states.CCW_AB, states.CCW_A, states.UNDEFINED, states.START], # counterclockwise A transitions (01) -> 00, 11
]


class RotaryEncoder:
    def __init__(self, pin_a, pin_b, decoding=1, default_value=0):
        self.signal_a = Pin(pin_a, Pin.IN, Pin.PULL_UP)
        self.signal_b = Pin(pin_b, Pin.IN, Pin.PULL_UP)

        self.decoding = decoding

        self.signal_a.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.handle_change)
        self.signal_b.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.handle_change)

        self.state = states.UNDEFINED

        self.value = default_value
        self.debug_calls = 0

        self.handle_change()

    def handle_change(self, pin=None):
        code = (self.signal_a.value() << 1) | self.signal_b.value()
        new_state = TRANSITION_MATRIX[self.state][code]

        # clockwise
        if self.state == states.CW_B and new_state == states.START:
            self.value += 1
        elif self.decoding == 2 and self.state == states.CW_A and new_state == states.CW_AB:
            self.value += 1
        # counterclockwise
        if self.state == states.CCW_A and new_state == states.START:
            self.value -= 1
        elif self.decoding == 2 and self.state == states.CCW_B and new_state == states.CCW_AB:
            self.value -= 1

        self.state = new_state 
        self.debug_calls += 1
        

if __name__ == '__main__':
    import utime

    SIGNAL_A_PIN = 0
    SIGNAL_B_PIN = 0

    encoder = RotaryEncoder(SIGNAL_A_PIN, SIGNAL_B_PIN, decoding=2)
    last_value = encoder.value
    while True:
        if last_value != encoder.value:
            print(encoder.value, encoder.debug_calls)
            last_value = int(encoder.value)
        utime.sleep(0.01)