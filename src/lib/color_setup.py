from micropython import const
from machine import Pin, SPI
from drivers.ili9488 import ILI9488

SCREENSIZE = SCREEN_W, SCREEN_H = (480, 320)

# Modified these pins for my specific screen wiring of pico.
# Pin Configuration
LCD_DC = const(7)
LCD_RST = const(6)
LCD_CS = const(5)
LCD_CLK = const(2)
LCD_MOSI = const(3)
LCD_LED = const(8)

# Initialize pins
pin_rst = Pin(LCD_RST, Pin.OUT, value=1)
pin_dc = Pin(LCD_DC, Pin.OUT, value=1)
pin_cs = Pin(LCD_CS, Pin.OUT, value=1)
pin_led = Pin(LCD_LED, Pin.OUT, value=1)

# Initialize SPI (24 MHz max speed on pico)
BAUD_RATE = 24_000_000
spi = SPI(
    0, BAUD_RATE, sck=Pin(LCD_CLK), mosi=Pin(LCD_MOSI, Pin.OUT)
)
screen = ILI9488(spi, width=SCREEN_W, height=SCREEN_H, dc=pin_dc, cs=pin_cs, rst=pin_rst, usd=False)