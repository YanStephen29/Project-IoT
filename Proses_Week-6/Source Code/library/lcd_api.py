class LcdApi:
    """
    Generic LCD display driver base class.
    """

    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.display_enabled = True
        self.backlight_enabled = True # Asumsi backlight ada dan bisa dikontrol

    def clear(self):
        """Clear the display and set cursor to home position."""
        self.command(0x01) # Clear display command
        self.command(0x02) # Return home command (also clears DDRAM content sometimes, but safer to use 0x01 first)

    def home(self):
        """Set cursor to home position."""
        self.command(0x02) # Return home command

    def set_display_enabled(self, enable):
        """Enable or disable the display."""
        if enable:
            self.command(0x0C) # Display on, cursor off, blink off
        else:
            self.command(0x08) # Display off, cursor off, blink off
        self.display_enabled = enable

    def backlight_on(self):
        """Turn on the backlight."""
        # Implementasi spesifik I2C akan menangani ini
        self.backlight_enabled = True

    def backlight_off(self):
        """Turn off the backlight."""
        # Implementasi spesifik I2C akan menangani ini
        self.backlight_enabled = False

    def move_to(self, col, row):
        """Move cursor to the specified column and row."""
        # Alamat DDRAM untuk baris:
        # Baris 0: 0x00
        # Baris 1: 0x40
        # Baris 2: 0x00 + num_cols (untuk 20x4 LCD, ini 0x14)
        # Baris 3: 0x40 + num_cols (untuk 20x4 LCD, ini 0x54)
        # Note: Some LCDs might map memory differently for 4-line displays.
        # This implementation assumes typical 20x4 mapping with 20 chars per line.
        # For 4x20 LCDs:
        # Line 0: 0x00
        # Line 1: 0x40
        # Line 2: 0x00 + 20 = 0x14 (hex)
        # Line 3: 0x40 + 20 = 0x54 (hex)
        # Let's handle 16x2 and 20x4 separately for clarity, though num_cols helps.

        if row == 0:
            addr = 0x00 + col
        elif row == 1:
            addr = 0x40 + col
        elif row == 2:
            addr = 0x00 + self.num_cols + col # For 4-line displays, 3rd line often starts after 2nd line's address space
        elif row == 3:
            addr = 0x40 + self.num_cols + col # For 4-line displays, 4th line often starts after 3rd line's address space
        else:
            # Jika baris melebihi, mungkin reset ke baris terakhir atau error
            raise ValueError("Row out of range")

        self.command(0x80 | addr) # Set DDRAM address command

    def putstr(self, text):
        """Write a string to the display."""
        for char in text:
            self.write_char(ord(char))

    # Metode abstrak, harus diimplementasikan oleh sub-kelas
    def command(self, value):
        """Send a command to the LCD."""
        raise NotImplementedError

    def write_char(self, char_code):
        """Write a character to the LCD."""
        raise NotImplementedError
