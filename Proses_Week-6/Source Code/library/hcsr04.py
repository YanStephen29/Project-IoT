from machine import Pin, time_pulse_us
import time

class HCSR04:
    def __init__(self, trigger_pin, echo_pin, echo_timeout_us=30000):
        self.trigger = Pin(trigger_pin, mode=Pin.OUT, pull=None)
        self.echo = Pin(echo_pin, mode=Pin.IN, pull=None)
        self.echo_timeout_us = echo_timeout_us
        self.trigger.value(0)
        time.sleep_ms(50)

    def distance_cm(self):
        self.trigger.value(0)
        time.sleep_us(2)
        self.trigger.value(1)
        time.sleep_us(10)
        self.trigger.value(0)
        try:
            pulse_time = time_pulse_us(self.echo, 1, self.echo_timeout_us)
            distance = (pulse_time / 2) / 29.1
            return distance
        except OSError as ex:
            if ex.args[0] == 110:  # timeout
                return None
            raise ex

