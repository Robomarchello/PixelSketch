from lib.utils import file_exists
from config import CHUNK_SIZE


class SaveManager:
    # idea:
    # MAX_SAVES = 10
    # *create a folder for saves*
    # then you can just open the most recent one
    screen = None
    @classmethod
    def initialize(cls, screen):
        cls.screen = screen

    @classmethod
    def save_screen(cls):
        if cls.screen is None:
            raise ValueError('initialize screen first')
        
        # write save file
        with open('save.bin', 'wb') as file:
            file.write(cls.screen.mvb)

    @classmethod
    def write_to_screen(cls):
        if file_exists('save.bin'):
            with open('save.bin', 'rb') as file:
                while True:
                    chunk = file.read(CHUNK_SIZE)
                    if not chunk:
                        break

                    binary = bytearray(chunk)
                    pos = file.tell()
                    cls.screen.mvb[pos-CHUNK_SIZE:pos] = binary
        else:
            return False