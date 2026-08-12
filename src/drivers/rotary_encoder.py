# My rotary encoder implementation for RPI pico:)
#
# I first implemented this with a Gray-code state machine (my own design),
# which worked great on the breadboard. Once everything was soldered onto
# perfboard, the encoders started producing a different edge pattern than
# my state machine expected, so with AI's help I reworked the decoding logic
# to trigger off CLK edges directly instead. My original state-machine
# version is preserved in earlier commits.

import micropython
from machine import Pin, Timer
from utime import ticks_diff, ticks_us


class RotaryEncoder:
    DEBOUNCE_TIMER_MS = 50
    MIN_PULSE_US = 800

    def __init__(self, pin_a, pin_b, button_pin, decoding=1, default_value=0):
        self.signal_a = Pin(pin_a, Pin.IN, Pin.PULL_UP)
        self.signal_b = Pin(pin_b, Pin.IN, Pin.PULL_UP)
        self.button = Pin(button_pin, Pin.IN, Pin.PULL_UP)

        self.decoding = decoding
        self.value = default_value
        self.button_pressed = False
        self.debounce_timer = Timer(-1)
        self.func = None

        self._last_clk = self.signal_a.value()
        self._last_pulse_us = 0

        self.enable_irq()

    def enable_irq(self):
        self.signal_a.irq(
            trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING,
            handler=self._handle_rot_change
        )
        self.button.irq(
            trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING,
            handler=self._handle_button_change
        )

    def disable_irq(self):
        self.signal_a.irq(handler=None)
        self.button.irq(handler=None)
        self.button_pressed = False

    def _handle_rot_change(self, pin=None):
        clk = self.signal_a.value()
        if clk == self._last_clk:
            return
        self._last_clk = clk

        if clk == 0:  # act only on CLK falling edge
            now = ticks_us()
            if ticks_diff(now, self._last_pulse_us) < self.MIN_PULSE_US:
                return  # debounce
            self._last_pulse_us = now

            dt = self.signal_b.value()
            if dt == 1:
                self.value -= 1
            else:
                self.value += 1

    def _debounce_callback(self, timer):
        stable_state = not self.button.value()

        if stable_state != self.button_pressed:
            self.button_pressed = stable_state
            if self._on_change is not None:
                try:
                    self._scheduled = True
                    micropython.schedule(self._on_change, 0)
                except RuntimeError:
                    self._scheduled = False

    def _on_change(self, arg):
        if self.func is not None:
            self.func()

    def _handle_button_change(self, pin):
        self.debounce_timer.init(
            mode=Timer.ONE_SHOT,
            period=self.DEBOUNCE_TIMER_MS,
            callback=self._debounce_callback,
        )


if __name__ == '__main__':
    import utime

    SIGNAL_A_PIN = 20
    SIGNAL_B_PIN = 19
    BUTTON_PIN = 13

    encoder = RotaryEncoder(SIGNAL_A_PIN, SIGNAL_B_PIN, BUTTON_PIN, decoding=1)

    def test_func():
        global encoder
        if encoder.button_pressed:
            print('button pressed')
        else:
            print('button unpressed')

    encoder.func = test_func
    last_value = encoder.value
    while True:
        if last_value != encoder.value:
            print(encoder.value)
            last_value = int(encoder.value)
        utime.sleep(0.01)