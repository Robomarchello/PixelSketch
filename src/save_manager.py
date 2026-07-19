from config import CHUNK_SIZE
from src.screen_manager import ScreenManager


class SaveManager:
    # idea:
    # MAX_SAVES = 10
    # *create a folder for saves*
    # then you can just open the most recent one
    screen = None
    SAVE_PATH = '/save.bin'
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
        ScreenManager.write_image_to_screen(cls.SAVE_PATH)