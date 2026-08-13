from states.state import State
import states.unlock
from input_manager import InputManager
from screen_manager import ScreenManager
from config import *
from secret import WIFI_NAME, WIFI_PASSWORD


class DebugState(State):
    CONNECT_TIMEOUT_MS = 15000
    NO_CREDS_MESSAGE_MS = 3000

    def __init__(self, state_machine):
        self.state_machine = state_machine

        self.screen = ScreenManager.screen
        self.colors = ScreenManager.COLORS

    @classmethod
    def initialize_network(cls):
        # Run once, manually, to set the WebREPL password on-device.
        # Not called during normal app flow.
        import webrepl_setup

    def logic(self):
        pass

    def _return_to_unlock(self):
        InputManager.enable_input()
        state = states.unlock.UnlockState(self.state_machine)
        self.state_machine.change_state(state)

    def on_enter(self):
        if WIFI_NAME is None or WIFI_PASSWORD is None:
            self.screen.fill(self.colors['BLACK'])
            self.screen.text('No WiFi creds set', 10, 10, self.colors['WHITE'])
            self.screen.text('Skipping debug mode', 10, 30, self.colors['WHITE'])
            self.screen.show()

            import utime
            utime.sleep_ms(self.NO_CREDS_MESSAGE_MS)

            self._return_to_unlock()
            return

        self.screen.fill(self.colors['BLACK'])
        self.screen.text('Connecting...', 10, 10, self.colors['WHITE'])
        self.screen.show()

        import network
        import utime

        wlan = network.WLAN(network.STA_IF)
        network.country('UA')
        wlan.active(True)
        wlan.connect(WIFI_NAME, WIFI_PASSWORD)

        start = utime.ticks_ms()
        while not wlan.isconnected():
            if utime.ticks_diff(utime.ticks_ms(), start) > self.CONNECT_TIMEOUT_MS:
                self.screen.fill(self.colors['BLACK'])
                print(wlan.status())
                self.screen.text('Connect failed', 10, 10, self.colors['WHITE'])
                self.screen.text('Hold btn to exit', 10, 30, self.colors['WHITE'])
                self.screen.show()
                print("WiFi connect timed out")
                return
            utime.sleep_ms(100)

        ip = wlan.ifconfig()[0]
        print("Connected! IP Address:", ip)

        InputManager.disable_input()
        import webrepl
        webrepl.start()

        self.screen.fill(self.colors['BLACK'])
        self.screen.text('Connected!', 10, 10, self.colors['WHITE'])
        self.screen.text(ip, 10, 30, self.colors['WHITE'])
        self.screen.text('WebREPL active', 10, 50, self.colors['WHITE'])
        self.screen.show()

    def on_exit(self):
        InputManager.enable_input()