# ILI9488 nano-gui driver for ili9488 displays

### Based on ili9486.py by Peter Hinch.
### Retaining his copyright

# Copyright (c) Peter Hinch 2022-2025
# Released under the MIT license see LICENSE

# This driver, adapted from ILI9486, was contributed by Carl Pottle (cpottle9).

# Note: If your hardware uses the ILI9488 parallel interface
# you will likely be better off using the ili9486 driver.
# It will send 2 bytes per pixel which will run faster.
#
# You must use this driver only when using the ILI9488 SPI
# interface. It will send 3 bytes per pixel.

# ILI9488 max SPI baudrate 20MHz (datasheet 17.4.3) but 24MHz is a reasonable overclock.

from time import sleep_ms
import gc
import framebuf
import asyncio
from drivers.boolpalette import BoolPalette

# Do processing from end to beginning for
# small performance improvement.
# greyscale
@micropython.viper
def _lcopy_gs(dest: ptr8, source: ptr8, length: int):
    # rgb666 - 18bit/pixel
    n: int = length * 6 - 1
    while length:
        length -= 1
        c: uint = source[length]
        # Store the index in the 4 high order bits
        p: uint = c & 0xF0  # current pixel
        q: uint = c << 4  # next pixel

        dest[n] = q
        n -= 1
        dest[n] = q
        n -= 1
        dest[n] = q
        n -= 1

        dest[n] = p
        n -= 1
        dest[n] = p
        n -= 1
        dest[n] = p
        n -= 1


# Do processing from end to beginning for
# small performance improvement.
# color
@micropython.viper
def _lcopy(dest: ptr8, source: ptr8, lut: ptr16, length: int):
    # Convert lut rgb 565 to rgb666
    n: int = length * 6 - 1
    while length:
        length -= 1
        c: uint = source[length]

        v = lut[c & 0x0F]  # next pixel
        dest[n] = (v & 0x001F) << 3  # B
        n -= 1
        dest[n] = (v & 0x07E0) >> 3  # G
        n -= 1
        dest[n] = (v & 0xF800) >> 8  # R
        n -= 1

        v: uint = lut[c >> 4]  # current pixel
        dest[n] = (v & 0x001F) << 3  # B
        n -= 1
        dest[n] = (v & 0x07E0) >> 3  # G
        n -= 1
        dest[n] = (v & 0xF800) >> 8  # R
        n -= 1


class ILI9488(framebuf.FrameBuffer):

    lut = bytearray(32)
    COLOR_INVERT = 0

    # Convert r, g, b in range 0-255 to a 16 bit colour value
    # 5-6-5 format
    #  byte order not swapped (compared to ili9486 driver).
    @classmethod
    def rgb(cls, r, g, b):
        return cls.COLOR_INVERT ^ ((r & 0xF8) << 8 | (g & 0xFC) << 3 | (b >> 3))

    # Transpose width & height for landscape mode
    def __init__(
        self,
        spi,
        cs,
        dc,
        rst,
        height=320,
        width=480,
        usd=False,
        mirror=False,
        init_spi=False,
        lines_per_write=4,
    ):
        self._spi = spi
        self._cs = cs
        self._dc = dc
        self._rst = rst
        self.lock_mode = False  # If set, user lock is passed to .do_refresh
        self.height = height  # Logical dimensions for GUIs
        self.width = width
        self._spi_init = init_spi
        self._gscale = False  # Interpret buffer as index into color LUT
        self.mode = framebuf.GS4_HMSB
        self.palette = BoolPalette(self.mode)
        #
        # lines_per_write must divide evenly into height
        #
        if (self.height % lines_per_write) != 0:
            raise ValueError("lines_per_write invalid")
        self._lines_per_write = lines_per_write
        gc.collect()
        buf = bytearray(height * width // 2)
        self.mvb = memoryview(buf)
        super().__init__(buf, width, height, self.mode)  # Logical aspect ratio
        self._linebuf = bytearray(self._lines_per_write * self.width * 3)

        # Hardware reset
        self._rst(0)
        sleep_ms(50)
        self._rst(1)
        sleep_ms(50)
        if self._spi_init:  # A callback was passed
            self._spi_init(spi)  # Bus may be shared
        self._lock = asyncio.Lock()
        # Send initialization commands

        self._wcmd(b"\x01")  # SWRESET Software reset
        sleep_ms(100)
        self._wcmd(b"\x11")  # sleep out
        sleep_ms(20)
        self._wcd(b"\x3a", b"\x66")  # interface pixel format 18 bits per pixel

        self._wcd(b"\x2a", int.to_bytes(self.width - 1, 4, "big"))
        self._wcd(b"\x2b", int.to_bytes(self.height - 1, 4, "big"))  # SET_PAGE ht

        if self.width > self.height:
            # landscape
            madctl = 0xE8 if usd else 0x28
        else:
            # portrait
            madctl = 0x48 if usd else 0x88
        if mirror:
            madctl ^= 0x80  # toggle MY
        self._wcd(b"\x36", madctl.to_bytes(1, "big"))  # MADCTL: RGB portrait mode
        self._wcmd(b"\x11")  # sleep out
        self._wcmd(b"\x29")  # display on

    # Code for 16 px text for micropython framebuf.
    # Thanks a lot Peter! :)
    # https://github.com/peter-l5/framebuf2
    # frambuf2 v209: micropython framebuffer extensions
    # (c) 2022-2023 Peter Lumb (peter-l5)
    def _reverse(self, s: string) -> string:
        t = ""
        for i in range(0, len(s)):
            t += s[len(s) - 1 - i]
        return t

    def large_text(self, s, x, y, m, c: int = 1, r: int = 0, t=None):
        """
        large text drawing function uses the standard framebuffer font (8x8 pixel characters)
        writes text, s,
        to co-cordinates x, y
        size multiple, m (integer, eg: 1,2,3,4. a value of 2 produces 16x16 pixel characters)
        colour, c [optional parameter, default value c=1]
        optional parameter, r is rotation of the text: 0, 90, 180, or 270 degrees
        optional parameter, t is rotation of each character within the text: 0, 90, 180, or 270 degrees
        """
        colour = c
        smallbuffer = bytearray(8)
        letter = framebuf.FrameBuffer(smallbuffer, 8, 8, framebuf.MONO_HMSB)
        r = r % 360 // 90
        dx = 8 * m if r in (0, 2) else 0
        dy = 8 * m if r in (1, 3) else 0
        if r in (2, 3):
            s = self._reverse(s)
        t = r if t is None else t % 360 // 90
        a, b, c, d = 1, 0, 0, 1
        for i in range(0, t):
            a, b, c, d = c, d, -a, -b
        x0 = 0 if a + c > 0 else 7
        y0 = 0 if b + d > 0 else 7
        for character in s:
            letter.fill(0)
            letter.text(character, 0, 0, 1)
            for i in range(0, 8):
                for j in range(0, 8):
                    if letter.pixel(i, j) == 1:
                        p = x0 + a * i + c * j
                        q = y0 + b * i + d * j
                        if m == 1:
                            self.pixel(x + p, y + q, colour)
                        else:
                            self.fill_rect(x + p * m, y + q * m, m, m, colour)
            x += dx
            y += dy
            
    # Write a command.
    def _wcmd(self, command):
        self._dc(0)
        self._cs(0)
        self._spi.write(command)
        self._cs(1)

    # Write a command followed by a data arg.
    def _wcd(self, command, data):
        self._dc(0)
        self._cs(0)
        self._spi.write(command)
        self._cs(1)
        self._dc(1)
        self._cs(0)
        self._spi.write(data)
        self._cs(1)

    def greyscale(self, gs=None):
        if gs is not None:
            self._gscale = gs
        return self._gscale

    # @micropython.native  # Made almost no difference to timing
    def show(self):  # Physical display is in portrait mode
        lb = self._linebuf
        buf = self.mvb
        cm = self._gscale  # color False, greyscale True
        if self._spi_init:  # A callback was passed
            self._spi_init(self._spi)  # Bus may be shared
        self._wcmd(b"\x2c")  # WRITE_RAM
        self._dc(1)
        self._cs(0)
        wd = self.width >> 1
        ht = self.height
        spi_write = self._spi.write
        length = self._lines_per_write * wd
        r = range(0, wd * ht, length)
        if cm:
            lcopy = _lcopy_gs  # Copy greyscale
            for start in r:  # For each line
                lcopy(lb, buf[start:], length)
                spi_write(lb)
        else:
            clut = ILI9488.lut
            lcopy = _lcopy  # Copy and map colors
            for start in r:  # For each line
                lcopy(lb, buf[start:], clut, length)
                spi_write(lb)
        self._cs(1)

    def show_region(self, x, y, w, h):
        """
        Update pixels only in the specified rectangular region of the display
        """
        # Asked Gemini to write this function. 
        # Works good for its purpose. Glad I have this tool:)
        # Way faster than updating whole screen.
        
        # 1. Align x and w to even numbers for GS4_HMSB (2 pixels per byte)
        x &= ~1
        w = (w + 1) & ~1
        
        # 2. Boundary clamping
        if x < 0: x = 0
        if y < 0: y = 0
        if x + w > self.width: w = self.width - x
        if y + h > self.height: h = self.height - y
        if w <= 0 or h <= 0: return

        # 3. Set the Address Window (Column and Row)
        # Column address set: x_start, x_end
        self._wcd(b"\x2a", (x).to_bytes(2, "big") + (x + w - 1).to_bytes(2, "big"))
        # Row address set: y_start, y_end
        self._wcd(b"\x2b", (y).to_bytes(2, "big") + (y + h - 1).to_bytes(2, "big"))

        # 4. Prepare for SPI transfer
        lb = self._linebuf
        buf = self.mvb
        cm = self._gscale  # color False, greyscale True
        
        if self._spi_init:
            self._spi_init(self._spi)

        self._wcmd(b"\x2c")  # WRITE_RAM
        self._dc(1)
        self._cs(0)
        
        spi_write = self._spi.write
        clut = ILI9488.lut
        lcopy = _lcopy_gs if cm else _lcopy
        
        # 5. Calculate row parameters
        # Row width in bytes for the source buffer
        full_row_bytes = self.width >> 1
        # Offset to the start of the region in bytes
        start_offset_bytes = (y * full_row_bytes) + (x >> 1)
        # Bytes per row to copy for the partial update
        bytes_to_copy = w >> 1
        
        # 6. Stream row by row
        try:
            for i in range(h):
                # Calculate source pointer for this row
                start = start_offset_bytes + (i * full_row_bytes)
                
                # Convert the partial row into _linebuf
                if cm:
                    lcopy(lb, buf[start:], bytes_to_copy)
                else:
                    lcopy(lb, buf[start:], clut, bytes_to_copy)
                
                # Write the converted 18-bit data (3 bytes per pixel)
                spi_write(lb[:w * 3])
        finally:
            self._cs(1)
            
            # 7. Restore the default window to full screen 
            # (Ensures normal .show() calls still work correctly)
            self._wcd(b"\x2a", (0).to_bytes(2, "big") + (self.width - 1).to_bytes(2, "big"))
            self._wcd(b"\x2b", (0).to_bytes(2, "big") + (self.height - 1).to_bytes(2, "big"))

    def short_lock(self, v=None):
        if v is not None:
            self.lock_mode = v  # If set, user lock is passed to .do_refresh
        return self.lock_mode

    # nanogui apps typically call with no args. ugui and tgui pass split and
    # may pass a Lock depending on lock_mode
    async def do_refresh(self, split=4, elock=None):
        if elock is None:
            elock = asyncio.Lock()
        async with self._lock:
            lines, mod = divmod(self.height, split)  # Lines per segment
            if mod:
                raise ValueError("Invalid do_refresh arg 'split'")
            if lines % self._lines_per_write != 0:
                raise ValueError(
                    "Invalid do_refresh arg 'split' for lines_per_write of %d"
                    % (self._lines_per_write)
                )
            clut = ILI9488.lut
            lb = self._linebuf
            buf = self.mvb
            cm = self._gscale  # color False, greyscale True
            self._wcmd(b"\x2c")  # WRITE_RAM
            self._dc(1)
            wd = self.width // 2
            line = 0
            spi_write = self._spi.write
            length = self._lines_per_write * wd
            for _ in range(split):  # For each segment
                async with elock:
                    if self._spi_init:  # A callback was passed
                        self._spi_init(self._spi)  # Bus may be shared
                    self._cs(0)
                    r = range(wd * line, wd * (line + lines), length)
                    if cm:
                        lcopy = _lcopy_gs  # Copy and greyscale
                        for start in r:
                            lcopy(lb, buf[start:], length)
                            spi_write(lb)
                    else:
                        lcopy = _lcopy  # Copy and map colors
                        for start in r:
                            lcopy(lb, buf[start:], clut, length)
                            spi_write(lb)

                    line += lines
                    self._cs(1)  # Allow other tasks to use bus
                await asyncio.sleep_ms(0)
