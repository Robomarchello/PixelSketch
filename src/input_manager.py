from drivers.rotary_encoder import RotaryEncoder
from config import * 

class InputManager:
    encoder_left = RotaryEncoder(
        pin_a=ENCODER_L_CLK,
        pin_b=ENCODER_L_DT,
        button_pin=ENCODER_L_SW,
        decoding=1
    )
    encoder_right = RotaryEncoder(
        pin_a=ENCODER_R_CLK,
        pin_b=ENCODER_R_DT,
        button_pin=ENCODER_R_SW,
        decoding=1
    )