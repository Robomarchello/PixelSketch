# !!! Idea scrapped for now.
# Honestly a little tired and this is not in a priority for now.
import json
import utime


class DrawTime:
    SLOTS = 5
    screen = None
    SAVE_PATH = '/gallery/save.json'

    start_ticks = 0
    slot_draw_time = {}
    
    @classmethod
    def initialize_save(cls):
        slot_draw_time = [None for _ in range(SLOTS)]

        with open(cls.SAVE_PATH, mode='w') as file:
            json.dump(slot_draw_time, file)

    @classmethod
    def start(cls, slot_id):
        cls.start_ticks = utime.ticks_ms()

    @classmethod
    def end(cls):
        elapsed_ms = utime.ticks_diff(utime.ticks_ms(), cls.start_ticks)

    @classmethod
    def read_slot_formatted(cls):
        pass