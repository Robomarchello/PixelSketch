from machine import Pin, I2C
from drivers.imu import MPU6050
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

    # motion sensor
    _i2c = I2C(1, scl=Pin(27), sda=Pin(26), freq=100000)
    _devices = _i2c.scan()
    motion_sensor = MPU6050(_i2c)

    # Configure optional settings (sensitivities)
    # accel_range options: 0 (+/-2g), 1 (+/-4g), 2 (+/-8g), 3 (+/-16g)
    # gyro_range options: 0 (+/-250 deg/s), 1 (+/-500 deg/s), 2 (+/-1000 deg/s), 3 (+/-2000 deg/s)
    motion_sensor.accel_range = 0
    # motion_sensor.gyro_range = 0 # we need only accel

    @classmethod
    def disable_input(cls):
        cls.encoder_left.disable_irq()
        cls.encoder_right.disable_irq()

    @classmethod
    def enable_input(cls):
        cls.encoder_left.enable_irq()
        cls.encoder_right.enable_irq()