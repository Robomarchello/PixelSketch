import struct
from machine import Pin, SPI
from drivers.ili9488 import ILI9488
from config import *


class ScreenManager:
    # Initialize pins
    pin_rst = Pin(LCD_RST, Pin.OUT, value=1)
    pin_dc = Pin(LCD_DC, Pin.OUT, value=1)
    pin_cs = Pin(LCD_CS, Pin.OUT, value=1)
    pin_led = Pin(LCD_LED, Pin.OUT, value=1)

    # Initialize SPI
    spi = SPI(
        0, BAUD_RATE, sck=Pin(LCD_CLK), mosi=Pin(LCD_MOSI, Pin.OUT)
    )
    screen = ILI9488(spi, width=SCREEN_W, height=SCREEN_H, dc=pin_dc, cs=pin_cs, rst=pin_rst, usd=False)

    # Color setup
    COLORS_SETUP = [
        ("BLACK", screen.rgb(0, 0, 0)), 
        ("WHITE", screen.rgb(255, 255, 255)), 
        ("RED", screen.rgb(255, 0, 0)), 
        ("GREEN", screen.rgb(0, 255, 0)), 
        ("BLUE", screen.rgb(0, 0, 255)),
    ]

    # Populate lookup table
    COLORS = {}
    for index, (color_name, color_value) in enumerate(COLORS_SETUP):
        struct.pack_into("<H", screen.lut, index * 2, color_value)
        COLORS[color_name] = index

    @classmethod
    def set_backlight_value(cls, value):
        # goal with this
        cls.pin_led.value(value)