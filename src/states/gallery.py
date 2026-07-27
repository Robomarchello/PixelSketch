import time
import os
def file_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False

from machine import ADC, Pin
from states.state import State
import states.drawing
from screen_manager import ScreenManager
from input_manager import InputManager
from config import *


class BatteryMeter:
    conversion_factor = (3.3 / 65535) * 3 # modify!!
    VOLTAGE_LEVELS = (
        (4.08, 100),
        (3.98, 90),
        (3.88, 80),
        (3.80, 70),
        (3.73, 60),
        (3.68, 50),
        (3.61, 40),
        (3.53, 30),
        (3.42, 20),
        (3.35, 10),
    )
    def __init__(self):
        self.screen = ScreenManager.screen
        self.COLORS = ScreenManager.COLORS

        self.battery_pin = Pin(BATTERY_READING_PIN, mode=Pin.IN)
        self.adc = ADC(self.battery_pin)

        self.cell_count = 5
        self.charge_per_cell = 100 // self.cell_count
        
        self.voltage = 0.0
        self.battery_level = 0
        self.cells_filled = 0

        # for drawing
        self.bat_position = (417, 289)
        self.cell_size = (8, 20)
        self.x_spacing = 2
        self.spacing_total = self.cell_size[0] + self.x_spacing

    def draw(self):
        self.screen.fill_rect(
            self.bat_position[0], 
            self.bat_position[1], 
            (self.cell_size[0] + self.x_spacing) * self.cell_count, 
            self.cell_size[1], 
            self.COLORS['BLACK']
        )

        for i in range(self.cells_filled):
            x_offset = self.spacing_total * i
            self.screen.fill_rect(
                self.bat_position[0] + x_offset, 
                self.bat_position[1], 
                self.cell_size[0], 
                self.cell_size[1], 
                self.COLORS['WHITE']
            )

        self.screen.show_region(
            self.bat_position[0], 
            self.bat_position[1], 
            (self.cell_size[0] + self.x_spacing) * self.cell_count, 
            self.cell_size[1], 
        )

    def get_voltage(self):
        raw_reading = self.adc.read_u16()
        
        self.voltage = raw_reading * self.conversion_factor
        print(f"VSYS Input Voltage: {self.voltage:.2f} V")

    def get_voltage(self):
        # DUMMY FUNCTION!!!
        print('dummy')
        self.voltage = 3.9
        self.voltage_to_battery_level()

    def voltage_to_battery_level(self):
        for voltage, charge in self.VOLTAGE_LEVELS:
            if self.voltage > voltage:
                self.battery_level = charge
                self.cells_filled = self.battery_level // self.charge_per_cell
                return
        self.battery_level = 0


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
        self.encoder_right.func = self.delete_file

        self.last_encoder_x = int(self.encoder_left.value)
        self.last_encoder_y = int(self.encoder_right.value)

        self.preview_topleft = (120, 95)
        self.infobar_topleft = (116, 
                                self.preview_topleft[1] + SCREEN_H // 2 + 10)
        self.infobar_size = (SCREEN_W // 2 + 10, 16)

        self.slot_path = None
        self.file_exists = False

        self.redraw_info = True

        self.battery_meter = BatteryMeter()

    def delete_file(self):
        if self.file_exists:
            os.remove(self.slot_path)

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

            self.battery_meter.draw()

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
        self.update_file_info()
        ScreenManager.write_image_to_screen(self.UI_path)
        ScreenManager.screen.show()

        InputManager.enable_input()

        self.battery_meter.get_voltage()

    def on_exit(self):
        InputManager.disable_input()
    