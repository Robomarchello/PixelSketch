# My rotary encoder implementation for RPI pico:)
import micropython
from machine import Pin, Timer

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
    DEBOUNCE_TIMER_MS = 50
    def __init__(self, pin_a, pin_b, button_pin, decoding=1, default_value=0):
        self.signal_a = Pin(pin_a, Pin.IN, Pin.PULL_UP)
        self.signal_b = Pin(pin_b, Pin.IN, Pin.PULL_UP)
        self.button = Pin(button_pin, Pin.IN, Pin.PULL_UP)

        self.decoding = decoding

        self.signal_a.irq(
            trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, 
            handler=self._handle_rot_change
        )
        self.signal_b.irq(
            trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, 
            handler=self._handle_rot_change
        )
        self.button.irq(
            trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, 
            handler=self._handle_button_change
        )

        self.state = states.UNDEFINED

        self.value = default_value
        self.debug_calls = 0

        # True = Pressed, False = Released
        self.button_pressed = False
        # Allocate a single timer instance upfront
        self.debounce_timer = Timer(-1)

        self.func = None
        
        self._handle_rot_change()

    def _debounce_callback(self, timer):
        stable_state = not self.button.value()

        if stable_state != self.button_pressed:
            self.button_pressed = stable_state
            if self._on_change is not None:
                micropython.schedule(self._on_change, ())
                
    def _on_change(self, arg):
        if self.func is not None:
            self.func()

    def _handle_button_change(self, pin):
        self.debounce_timer.init(
            mode=Timer.ONE_SHOT,
            period=self.DEBOUNCE_TIMER_MS,
            callback=self._debounce_callback,
        )

    def _handle_rot_change(self, pin=None):
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
    BUTTON_PIN = 0

    def test_func(encoder):
        if encoder.button_pressed:
            print('button pressed')
        else:
            print('button unpressed')

    encoder = RotaryEncoder(SIGNAL_A_PIN, SIGNAL_B_PIN, BUTTON_PIN, decoding=2)
    encoder.func = test_func
    last_value = encoder.value
    while True:
        if last_value != encoder.value:
            print(encoder.value, encoder.debug_calls)
            last_value = int(encoder.value)
        utime.sleep(0.01)