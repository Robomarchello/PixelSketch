# --- Screen configuration
SCREEN_SIZE = SCREEN_W, SCREEN_H = 480, 320
# display pins
LCD_DC = const(7)
LCD_RST = const(6)
LCD_CS = const(5)
LCD_CLK = const(2)
LCD_MOSI = const(3)
LCD_LED = const(8)
# screen spi (24 MHz max speed on pico)
BAUD_RATE = 24_000_000

ENCODER_L_CLK, ENCODER_L_DT, ENCODER_L_SW = 12, 13, 10
ENCODER_R_CLK, ENCODER_R_DT, ENCODER_R_SW = 18, 19, 21

BRUSH_RADIUS = 3
BG_COLOR = 'WHITE'

CHUNK_SIZE = 512
