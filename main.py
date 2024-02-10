"""

VL53L0X_TOF_Sensor

basics for VL53L0X Time Of Flight sensor

"""

from time import sleep
import board
import busio

from adafruit_vl53l0x import VL53L0X


class MultiMeasurementUnitTOF(VL53L0X):
    valid_units = ['in', 'mm', 'cm']

    def __init__(self, units: str = None, *args, **kwargs):
        if units:
            self._units = units
        super().__init__(*args, **kwargs)
        self._range_allowed = None
        self._max_range = None
        self._min_range = None
        self._last_range = None
        self._range_has_changed = False

    @property
    def units(self):
        return self._units

    @units.setter
    def units(self, value):
        for k in self.valid_units:
            if value.lower() == k:
                self._units = value.lower()
        else:
            self._units = 'mm'

    @property
    def max_range(self):
        if self._units == 'mm':
            self._max_range = 1000  # really about 1000mm, but reads at 8190
        elif self._units == 'cm':
            self._max_range = 100
        elif self._units == 'in':
            self._max_range = 39.37

        return self._max_range

    @property
    def min_range(self):
        if self._units == 'mm':
            self._min_range = 30
        elif self._units == 'cm':
            self._min_range = 3
        elif self._units == 'in':
            self._min_range = 1.81

        return self._min_range

    @property
    def range_allowed(self):
        if self._units == 'mm':
            self._range_allowed = 5
        elif self._units == 'cm':
            self._range_allowed = 0.5
        elif self._units == 'in':
            self._range_allowed = 0.197

        return self._range_allowed

    @property
    def converted_range(self):
        # TODO: if the range isn't within upper or lower bounds then return the error str
        if self._units == 'mm':
            return self.range
        elif self._units == 'cm':
            return self.range_centimeters
        elif self._units == 'in':
            return self.range_inches
        else:
            return self.range

    @property
    def range_inches(self):
        return round((self.range / 25.4), 2)

    @property
    def range_centimeters(self):
        return self.range / 10

    @property
    def range_has_changed(self):
        self._range_has_changed = False
        if self._last_range != self.range:
            if type(self._last_range) in [int, float]:
                range_diff = abs(self._last_range - self.converted_range)
                if range_diff > self.range_allowed:
                    self._range_has_changed = True
        return self._range_has_changed

    def print_continuously(self):
        printed_range = None
        printed_nothing_detected = None

        while True:
            if self.converted_range < self.max_range and (not printed_range or self.range_has_changed):
                print(f"current range is {self.converted_range} {self.units}")
                self._last_range = self.converted_range
                printed_range = True
                printed_nothing_detected = False
            elif self.max_range <= self.converted_range and not printed_nothing_detected:
                print(f"nothing detected or object is outside of detectable range ({self.min_range}-{self.max_range} {self.units}).")
                printed_nothing_detected = True
                printed_range = False
            sleep(0.2)


if __name__ == "__main__":
    i2c = busio.I2C(board.GP1, board.GP0)  # uses board.SCL and board.SDA
    tof = MultiMeasurementUnitTOF(units='cm', i2c=i2c)
    tof.print_continuously()
