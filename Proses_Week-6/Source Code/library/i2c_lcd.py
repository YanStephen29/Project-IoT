
# i2c_lcd.py
# (This file should be named 'i2c_lcd.py' and saved on your MicroPython device)

from machine import Pin, I2C
from time import sleep_us
from lcd_api import LcdApi

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_BACKLIGHT = 0x08  # On
# LCD_BACKLIGHT = 0x00  # Off

# LCD RAM address for the 1st line
LCD_LINE_1 = 0x80
# LCD RAM address for the 2nd line
LCD_LINE_2 = 0xC0
# LCD RAM address for the 3rd line
LCD_LINE_3 = 0x94 # For 4x20 LCDs, this is typically 0x80 + 20 (0x14)
# LCD RAM address for the 4th line
LCD_LINE_4 = 0xD4 # For 4x20 LCDs, this is typically 0xC0 + 20 (0x14)

# Timing constants
E_PULSE = 500  # microseconds for enable pulse
E_DELAY = 500  # microseconds delay after enable pulse

class I2cLcd(LcdApi):
    """
    Driver for Hitachi HD44780 compatible LCD displays connected via PCF8574 I2C adapter.
    """

    def __init__(self, i2c, i2c_addr, num_rows, num_cols):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.backlight = LCD_BACKLIGHT
        LcdApi.__init__(self, num_rows, num_cols)

        # Initialize the LCD
        self.write(0x03)
        self.write(0x03)
        self.write(0x03)
        self.write(0x02) # 4-bit mode

        self.command(0x28) # Function set: 4-bit, 2 or 4 lines, 5x8 dots (auto-detect rows)
        self.command(0x08) # Display control: Display off, cursor off, blink off
        self.command(0x01) # Clear display
        self.command(0x06) # Entry mode set: Increment cursor, no display shift
        self.command(0x0C) # Display on, cursor off, blink off

    def command(self, cmd):
        """Send a command to the LCD."""
        self.write(cmd & 0xF0) # High nibble
        self.write((cmd << 4) & 0xF0) # Low nibble

    def write_char(self, char_code):
        """Write a character to the LCD."""
        self.write(char_code & 0xF0 | LCD_CHR) # High nibble
        self.write((char_code << 4) & 0xF0 | LCD_CHR) # Low nibble

    def write(self, data, mode=LCD_CMD):
        """Write data to the I2C bus."""
        self.i2c.writeto(self.i2c_addr, bytes([data | mode | self.backlight]))
        self.toggle_enable(data | mode | self.backlight)

    def toggle_enable(self, data):
        """Toggle enable pin to send data."""
        sleep_us(E_DELAY)
        self.i2c.writeto(self.i2c_addr, bytes([data | 0x04])) # Enable high
        sleep_us(E_PULSE)
        self.i2c.writeto(self.i2c_addr, bytes([data & ~0x04])) # Enable low
        sleep_us(E_DELAY)

    def backlight_on(self):
        """Turn on the backlight."""
        self.backlight = LCD_BACKLIGHT
        self.i2c.writeto(self.i2c_addr, bytes([self.backlight]))

    def backlight_off(self):
        """Turn off the backlight."""
        self.backlight = 0x00
        self.i2c.writeto(self.i2c_addr, bytes([self.backlight]))
