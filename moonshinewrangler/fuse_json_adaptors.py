# python3
# fuse_json_adaptors.py
# Author: Tim Littlefair, October 2025-

# This file defines adaptor helper objects to assist with converting
# FUSE u16 parameter values to the corresponding JSON value (which may
# be fixed point or integer numeric, or may be an enumeration string),
# and also converting the JSON value to the corresponding value displayed
# on a device user interface.

# The majority of u16 FUSE parameters appear to match to JSON float values
# ranging over the domain 0.0-1.0.
# By a rough scan of the 45 .fuse files from the @intheblues Mustang Mondays
# dataset, u16 values 33024 (0x8100) and 65280 (0xFF00) are very common
# (204 and 112 occurrences respectively), while 65535 occurs 39 times in
# total (but usually always associated with the same parameter, index 9,
# "Noise Gate Depth" ).
# Based on this data, the present working hypothesis for converting
# these values is that u16 values in the range 0x0300-0xFF00 are mapped
# by linear interpolation to 0.0 to 1.0 (making 33024 map to 0.5 which
# is an expected frequent value), and that 65535 is reserved as a null
# indicator value used where the float is undefined.


class RangeAdaptor:

    def __init__(self, min_in, max_in, min_out, max_out, format=None, suffix=""):
        self.min_in = min_in
        self.max_in = max_in
        self.min_out = min_out
        self.max_out = max_out
        self.format = format
        self.suffix = suffix

    def adapt(self, value_in):
        assert value_in >= self.min_in
        assert value_in <= self.max_in
        numerator = ((value_in - self.min_in) * (self.max_out - self.min_out))
        denominator = (self.max_in - self.min_in)
        value_out = self.min_out + (numerator / denominator)
        value_out_str = None
        if self.format is not None:
            value_out_str = format(value_out, self.format)
        else:
            value_out_str = str(value_out)
        if isinstance(self.min_out, int):
            return int(value_out_str), value_out_str + self.suffix
        else:
            return float(value_out_str), value_out_str + self.suffix


# I choose to truncate continuous/float values in JSON to 3 decimal
# places on the grounds that:
# a) AFAIK there are no parameters where a different value at the
#    4th decimal place or later is likely to be perceptible to a
#    normal human listening to the preset; and
# b) quantizing values in this way will reduce the likelihood of
#    near-duplicate presets returning different hashes when a control
#    is nudged by an infinitisemal amount.
_DEFAULT_JSON_FORMAT = ".3f"


class ContinuousValuedParameterAdaptor:

    def __init__(
        self,
        fuse_min=0x0300, fuse_max=0xff00,
        json_min=0.0, json_max=1.0,
        ui_range_adaptors=None
    ):
        self.fuse_to_json = RangeAdaptor(fuse_min, fuse_max, json_min, json_max, _DEFAULT_JSON_FORMAT)
        if ui_range_adaptors is not None:
            self.ui_range_adaptors = ui_range_adaptors
        else:
            # Rendering of most of the continuous parameter values on FMIC's first
            # party UIs differs between:
            # + 1.0 to 10.0 (Fender Tone LT Desktop/LCD UI on Fender LT- series amp) or
            # + 0% to 100% (Fender Tone Mobile for Mustang Micro Plus).
            # The logic below is intended to display both
            self.ui_range_adaptors = (
                # LCD UI on LT- series and Fender Tone LT Desktop
                # feed back value for most params on range 1.0 to 10.0
                RangeAdaptor(min_in=0.0, max_in=1.0, min_out=1.0, max_out=10.0, format="2.1f"),
                # Fender Tone Mobile for MMP (probably also GT-, GTX-)
                # feed back value for most params on range 0% to 100%
                RangeAdaptor(min_in=0.0, max_in=1.0, min_out=0.0, max_out=100.0, format=".0f", suffix="%"),
            )

    def fuse_to_json(self, fuse_value):
        return self.fuse_to_json.adapt(fuse_value)

    def json_to_ui(self, json_value):
        ui_values = [
            ui_ra.adapt(json_value)[1]
            for ui_ra in self.ui_range_adaptors
        ]
        return "/".join(ui_values)


class StringChoiceParameterAdaptor:

    def __init__(
        self,
        json_strings,
        ui_strings
    ):
        self.json_strings = json_strings
        self.ui_strings = ui_strings
        self.fuse_to_json = lambda v: self.json_strings[v]
        self.json_to_ui = lambda v: self.ui_strings[v]


if __name__ == "__main__":

    # Minimal tests

    cvpa = ContinuousValuedParameterAdaptor()
    expect_zero_point_zero = cvpa.fuse_to_json.adapt(0x0300)[0]
    expect_zero_point_five = cvpa.fuse_to_json.adapt(0x8100)[0]  # aka decimal 33024
    expect_one_point_zero = cvpa.fuse_to_json.adapt(0xff00)[0]
    assert expect_zero_point_zero == 0.0, f"Expected 0.0, got {expect_zero_point_zero}"
    assert expect_zero_point_five == 0.5, f"Expected 0.5, got {expect_zero_point_five}"
    assert expect_one_point_zero == 1.0, f"Expected 0.1, got {expect_one_point_zero}"

    scpa = StringChoiceParameterAdaptor(
        ["red", "green", "blue"],
        {"red": "RED", "green": "GREEN", "blue": "BLUE"}
    )
    expect_red = scpa.fuse_to_json(0)
    expect_GREEN = scpa.json_to_ui("green")
    assert expect_red == "red", f"Expected 'red' got {expect_red}"
    assert expect_GREEN == "GREEN", f"Expected 'GREEN' got {expect_GREEN}"
