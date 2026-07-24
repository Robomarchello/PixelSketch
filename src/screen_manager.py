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
        ("GREEN", screen.rgb(42, 176, 21)), 
        ("BLUE", screen.rgb(30, 50, 200)),
        ("CYAN", screen.rgb(0, 245, 212)),
        ("YELLOW", screen.rgb(255, 209, 34)),
        ("PURPLE", screen.rgb(250, 3, 253)),
        ("UI_HG", screen.rgb(255, 106, 19)),
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

    @classmethod
    def write_image_to_screen(cls, file_path):
        with open(file_path, 'rb') as file: # type: ignore
            while True:
                chunk = file.read(CHUNK_SIZE)
                if not chunk:
                    break

                binary = bytearray(chunk)
                pos = file.tell()
                cls.screen.mvb[pos-CHUNK_SIZE:pos] = binary

    @classmethod
    def write_image_shunk(cls, file_path, start_pos):
        screen = cls.screen.mvb
        half_screen_w = SCREEN_W // 2 
        half_screen_h = SCREEN_H // 2
    
        index_pos =  (start_pos[0] + start_pos[1] * SCREEN_W ) // 2

        with open(file_path, 'rb') as file: # type: ignore
            for y in range(half_screen_h):
                row = file.read(half_screen_w)
                for x in range(0, half_screen_w - 1, 2):
                    position = (x + y * SCREEN_W ) // 2 + index_pos
                    screen[position] = (row[x] << 4) | row[x + 1]
                file.seek(y * SCREEN_W)