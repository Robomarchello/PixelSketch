from PIL import Image

COLOR_INVERT = 0
def rgb(r, g, b):
    return COLOR_INVERT ^ ((r & 0xF8) << 8 | (g & 0xFC) << 3 | (b >> 3))

# Color palette. Get up-to-date colors_setup from screen_manager.py 
COLORS_SETUP = [
    ("BLACK", rgb(0, 0, 0)), 
    ("WHITE", rgb(255, 255, 255)), 
    ("RED", rgb(255, 0, 0)), 
    ("GREEN", rgb(0, 255, 0)), 
    ("BLUE", rgb(0, 0, 255)),
    ("UI_HG", rgb(255, 106, 19)),
]

# Populate lookup table
COLORS = {}
for index, (color_name, color_value) in enumerate(COLORS_SETUP):
    COLORS[color_value] = index

img = Image.open("ui_unlock.png").resize((480, 320))
img = img.convert("RGB")

with open("image_data.bin", "wb") as f:
    for y in range(img.height):
        for x in range(0, img.width, 2):
            r, g, b = img.getpixel((x, y))
            r1, g1, b1 = img.getpixel((x+1, y))
            # Convert 8-bit R, G, B channels down to 5-bit, 6-bit, and 5-bit
            color_index = COLORS[rgb(r, g, b)]
            color_index_1 = COLORS[rgb(r1, g1, b1)]
            
            color_lut_pair = (color_index << 4) | color_index_1

            f.write(bytes([color_lut_pair]))

print('done')