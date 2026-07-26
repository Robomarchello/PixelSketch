import time
import os
def file_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False
    
from states.state import State
import states.drawing
from screen_manager import ScreenManager
from input_manager import InputManager
from config import *


class GalleryState(State):
    UI_path = '/gallery.bin'
    SAVE_path = '/gallery/'
    SAVE_FOLDER_NAME = 'gallery'
    SLOTS = 5

    # I've put it here so even after exiting you get straight to the needed slot.
    slot_index = 0
    def __init__(self, state_machine):
        self.initialize_slots()
        
        self.state_machine = state_machine

        self.screen = ScreenManager.screen
        self.COLORS = ScreenManager.COLORS

        self.encoder_left = InputManager.encoder_left
        self.encoder_right = InputManager.encoder_right

        self.change_state = False
        self.encoder_left.func = self.open_draw_isr

        self.last_encoder_x = int(self.encoder_left.value)
        self.last_encoder_y = int(self.encoder_right.value)

        self.preview_topleft = (120, 95)
        self.infobar_topleft = (116, 
                                self.preview_topleft[1] + SCREEN_H // 2 + 10)
        self.infobar_size = (SCREEN_W // 2 + 10, 16)

        self.slot_path = None
        self.file_exists = False

        self.redraw_info = True

        self.update_file_info()

    def open_draw_isr(self):
        self.change_state = True

    def open_draw_state(self):
        if self.encoder_left.button_pressed:
            InputManager.disable_input()
            new_state = states.drawing.DrawingState(self.state_machine)

            new_state.file_exists = self.file_exists
            new_state.save_path = self.slot_path

            self.state_machine.change_state(new_state)

    def draw(self):
        curr_encoder_x = int(self.encoder_left.value)
        curr_encoder_y = int(self.encoder_right.value)

        # Calculate position change (deltas)
        dx = curr_encoder_x - self.last_encoder_x
        dy = -(curr_encoder_y - self.last_encoder_y)

        if dx != 0:
            self.toggle_slot(dx)
        elif dy != 0:
            self.toggle_slot(dy)

        self.last_encoder_x = curr_encoder_x
        self.last_encoder_y = curr_encoder_y

        if self.redraw_info:
            self.write_slot_img()
            self.draw_slot_info()

            self.redraw_info = False

        if self.change_state:
            self.open_draw_state()

    def write_slot_img(self):
        if self.file_exists:
            ScreenManager.write_image_shunk(self.slot_path, self.preview_topleft)
        else:
            ScreenManager.screen.fill_rect(
                self.preview_topleft[0], 
                self.preview_topleft[1], 
                SCREEN_W // 2, 
                SCREEN_H // 2, 
                self.COLORS['WHITE']
            )
        ScreenManager.screen.show_region(
            self.preview_topleft[0], 
            self.preview_topleft[1], 
            SCREEN_W // 2, 
            SCREEN_H // 2
        )

    def toggle_slot(self, change):
        step = 1 if change > 0 else -1
        self.slot_index = (self.slot_index + step) % self.SLOTS

        self.update_file_info()

    def update_file_info(self):
        self.slot_path = self.SAVE_path + f'slot_{self.slot_index}.bin'
        self.file_exists = file_exists(self.slot_path)
        self.redraw_info = True

    def draw_slot_info(self):
        ScreenManager.screen.fill_rect(
            self.infobar_topleft[0], 
            self.infobar_topleft[1], 
            self.infobar_size[0], 
            self.infobar_size[1], 
            self.COLORS['BLACK']
        )
        self._draw_slot_count()

        if self.file_exists:
            # Get the file statistics tuple
            file_stat = os.stat(self.slot_path)

            # Extract modification time (index 8)
            mtime = file_stat[8]

            # Convert the timestamp to a readable date tuple
            # Returns (year, month, mday, hour, minute, second, weekday, yearday)
            date_tuple = time.localtime(mtime)
            self._draw_date(date_tuple)
            
        else:
            self.screen.large_text(
                'NEW!', 
                self.infobar_topleft[0], 
                self.infobar_topleft[1], 
                2, 
                self.COLORS['WHITE']
            )
        ScreenManager.screen.show_region(
            self.infobar_topleft[0], 
            self.infobar_topleft[1], 
            self.infobar_size[0], 
            self.infobar_size[1]
        )

    def _draw_date(self, date_tuple):
        date_formatted = f'{date_tuple[2]}.{date_tuple[1]}.{date_tuple[0]}'
        self.screen.large_text(
            date_formatted, 
            self.infobar_topleft[0], 
            self.infobar_topleft[1], 
            1, 
            self.COLORS['WHITE']
        )

    def _draw_slot_count(self):
        slot_info = f'Slot {self.slot_index+1}/{self.SLOTS}'
        self.screen.large_text(
            slot_info, 
            295, 
            self.infobar_topleft[1], 
            1, 
            self.COLORS['WHITE']
        )

    def initialize_slots(self):
        if self.SAVE_FOLDER_NAME not in os.listdir():
            os.mkdir(self.SAVE_path)

    def on_enter(self):
        ScreenManager.write_image_to_screen(self.UI_path)
        ScreenManager.screen.show()

        InputManager.enable_input()

    def on_exit(self):
        InputManager.disable_input()
    