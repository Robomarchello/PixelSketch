import time
from machine import Pin, I2C
from drivers.imu import MPU6050, MPUException
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

    _i2c = I2C(1, scl=Pin(MOTION_SCL), sda=Pin(MOTION_SDA), freq=100000)

    motion_sensor = None
    _last_error = None
    for _attempt in range(6):
        try:
            _devices = _i2c.scan()
            print("I2C scan attempt {}: found {}".format(_attempt + 1, _devices))
            motion_sensor = MPU6050(_i2c)
            print("MPU6050 init succeeded on attempt {}".format(_attempt + 1))
            break
        except MPUException as e:
            _last_error = e
            print("MPU6050 init attempt {} failed: {}".format(_attempt + 1, e))
            time.sleep_ms(250)

    if motion_sensor is None:
        raise _last_error  # give up after 6 tries, surface the real error

    @classmethod
    def disable_input(cls):
        cls.encoder_left.disable_irq()
        cls.encoder_right.disable_irq()

    @classmethod
    def enable_input(cls):
        cls.encoder_left.enable_irq()
        cls.encoder_right.enable_irq()