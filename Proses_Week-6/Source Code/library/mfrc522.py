from machine import Pin, SPI
from os import uname
import time

class MFRC522:
    OK = 0
    NOTAGERR = 1
    ERR = 2

    REQIDL = 0x26
    AUTHENT1A = 0x60
    AUTHENT1B = 0x61

    def __init__(self, sck, mosi, miso, rst, cs):
        self.sck = Pin(sck, Pin.OUT)
        self.mosi = Pin(mosi, Pin.OUT)
        self.miso = Pin(miso, Pin.IN)
        self.rst = Pin(rst, Pin.OUT)
        self.cs = Pin(cs, Pin.OUT)

        self.spi = SPI(1, baudrate=1000000, polarity=0, phase=0,
                       sck=self.sck, mosi=self.mosi, miso=self.miso)

        self.rst.value(1)
        self.cs.value(1)

        self.init()

    def init(self):
        self.reset()
        self.write(0x2A, 0x8D)
        self.write(0x2B, 0x3E)
        self.write(0x2D, 30)
        self.write(0x2C, 0)
        self.write(0x15, 0x40)
        self.write(0x11, 0x3D)
        self.antenna_on()

    def reset(self):
        self.write(0x01, 0x0F)

    def write(self, reg, val):
        self.cs.value(0)
        self.spi.write(bytearray([(reg << 1) & 0x7E, val]))
        self.cs.value(1)

    def read(self, reg):
        self.cs.value(0)
        self.spi.write(bytearray([((reg << 1) & 0x7E) | 0x80]))
        val = self.spi.read(1)
        self.cs.value(1)
        return val[0]

    def set_bitmask(self, reg, mask):
        self.write(reg, self.read(reg) | mask)

    def clear_bitmask(self, reg, mask):
        self.write(reg, self.read(reg) & (~mask))

    def antenna_on(self):
        if ~(self.read(0x14) & 0x03):
            self.set_bitmask(0x14, 0x03)

    def request(self, req_mode):
        self.write(0x0D, 0x07)
        (status, back_data, back_len) = self.to_card(0x0C, [req_mode])
        if (status != self.OK) | (back_len != 0x10):
            status = self.ERR
        return status, back_data

    def anticoll(self):
        ser_num = []
        self.write(0x0D, 0x00)
        (status, back_data, back_bits) = self.to_card(0x0C, [0x93, 0x20])
        if status == self.OK:
            if len(back_data) == 5:
                ser_num = back_data
            else:
                status = self.ERR
        return status, ser_num

    def to_card(self, command, send_data):
        recv_data = []
        bits = 0
        status = self.ERR

        irq_en = 0x77
        wait_irq = 0x30
        self.write(0x02, irq_en | 0x80)
        self.clear_bitmask(0x04, 0x80)
        self.set_bitmask(0x0A, 0x80)
        self.write(0x01, 0x00)

        for c in send_data:
            self.write(0x09, c)
        self.write(0x01, command)

        if command == 0x0C:
            self.set_bitmask(0x0D, 0x80)

        i = 2000
        while True:
            n = self.read(0x04)
            i -= 1
            if not (i != 0 and not (n & 0x01) and not (n & wait_irq)):
                break

        self.clear_bitmask(0x0D, 0x80)

        if i != 0:
            if (self.read(0x06) & 0x1B) == 0x00:
                status = self.OK
                if n & irq_en & 0x01:
                    status = self.NOTAGERR
                if command == 0x0C:
                    length = self.read(0x0A)
                    bits = self.read(0x0C) & 0x07
                    if bits != 0:
                        bits = (length - 1) * 8 + bits
                    else:
                        bits = length * 8

                    for _ in range(length):
                        recv_data.append(self.read(0x09))
            else:
                status = self.ERR
        return status, recv_data, bits
