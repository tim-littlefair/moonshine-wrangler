#! python3

# Author: Tim Littlefair, 2026-
# The author licenses this progress to you under the MIT License
# See the file LICENSE in the base directory of the distribution for 
# full terms of this license.

"""
This script contains utilities for the analysis of publicly 
released firmware for various FMIC modelling amplifiers 
released over the period 2012-2017 with model numbers 
ending in roman numerals I to V with or without a 'v2' 
suffix.
"""

import binascii
import math
import zipfile

""" Firmware releases made prior to 2016 were done as files
with an .upd extension.
From 2016 onward, the releases were done as zip files 
containing a single member with a .upd extension.
We assume that the format within the upd stream did not 
change, this function wraps the two formats and retrieves
the .upd stream of bytes from either."""
def get_upd_stream(path):
    if(path.endswith(".upd")):
        return open(path).read()
    elif path.endswith(".zip"):
        zf = zipfile.ZipFile(path)
        assert len(zf.filelist)==1, zf.filelist
        assert zf.filelist[0].filename.endswith(".upd"), zf.filelist[0]
        return zf.open(zf.filelist[0]).read()

"""This script searches for any of a list of strings in the stream.
Each time a target string is found, the file offset is printed 
in hex and a hex dump is printed starting a fixed
number of bytes before the string.
"""
def find_strings_in_byte_stream(
    byte_stream, target_strings, bytes_before, buffer_length, clazz=None
):
    num_16byte_blocks=math.ceil(buffer_length/16)
    for s in target_strings:
        offset = 0
        s_bytes = s.encode("utf-8")

        offset = byte_stream.find(s_bytes, offset+1)
        if offset == -1:
            return None
        buffer = byte_stream[
            offset-bytes_before:
            offset-bytes_before+buffer_length
        ]
        buffer_hex = str(binascii.b2a_hex(buffer),"utf-8")
        end_offset = offset + buffer_length
        found_line = "\n".join(
            [f"{offset:08x} {s:20s}"] + 
            [f"{buffer_hex[n*32:(n+1)*32]}" for n in range(0,num_16byte_blocks)] +
            [f"{end_offset:08x}"]
        )
        # The clazz parameter is an optional type which can be used to 
        # instantiate a Python object containing the found string value.
        # If the parameter is not supplied, it is assumed that the function
        # is being used to generate guesses, a dump is printed and the offset
        # where the string was found is returned.
        if clazz is None:
            print(found_line)
            return offset
        else:
            return clazz(byte_stream,offset)


def nul_terminated_string(byte_string):
    first_nul_pos = byte_string.find(0)
    if first_nul_pos!=-1:
        byte_string = byte_string[0:first_nul_pos]
    return str(byte_string,"utf-8")

"""Based on the observations documented in function _preset_table_investigation(...)
I believe that the representation of presets in classic firmware is as follows:
+ bytes 0-19 preset name (all names in factory firmware are 7-bit ASCII, I don't 
  yet know whether any of UTF-8, iso-latin-1 or some Windows code page might be 
  supported)
+ byte 20: DSP module id for amp (single byte unsigned)
+ bytes 21-43: amp parameters (presumably)
+ byte 44: DSP module id for slot 0 effect (single byte unsigned)
+ bytes 45-61: parameters for slot 0 effect
+ bytes 62, 63-79: module id, parameters for slot 1 effect
+ bytes 80, 81-97: module id, parameters for slot 2 effect
+ bytes 98, 99-115: module id, parameters for slot 3 effect
"""
class ClassicPreset(dict):
    def __init__(self, byte_stream, offset):
        self.byte_stream = byte_stream[offset:offset+0x78]
        self["name"]=nul_terminated_string(self.byte_stream[0:20])
        self["amp_id"]=self.byte_stream[20]
        self["fx"] = [ self.byte_stream[44+(slot*18)] for slot in range(0,4)]

    def effect_id(self,slot):
        return self.byte_stream[44+(slot*18)]
    
class ClassicName:
    def __init__(self, byte_stream, offset, encoding="utf-8"):
        byte_stream=byte_stream[offset:]
        self.nts = nul_terminated_string(byte_stream)
        # The byte stream for the name includes the terminating NUL
        self.byte_stream=byte_stream[:len(self.nts)+1]
    def __str__(self):
        return self.nts

def _preset_table_investigation(upd_stream):
    print("\n    ".join([
        "Scan 1: scanning for the names of the following presets:",
        "#0 'Brutal Metal 2';",
        "#1 'Super-Live Album'",
        "#23: 'Chimey Deluxe'"
    ]));
    print("\n".join([
        "These are names of the first, second, and last(24th) presets defined in firmware",
        "for MustangIv2.",
        "Finding these enables us to make some guesses about the format of ",
        "the table of presets"
    ]))
    presets = find_strings_in_byte_stream(
        upd_stream, [
            "Brutal Metal II", 
            "Super-Live Album", 
            "Chimey Deluxe"
        ], 0x80, 0x200,None 
    )
    print("\n    ".join([
        "Observations from scan 1:",
        "TBD"
    ]))

    
if __name__ == "__main__":

    m1v2_upd_bytes = get_upd_stream("_work/reference_files/V2_Mustang1_2.2.zip")

    _preset_table_investigation(m1v2_upd_bytes)

    # The offset into the firmware of the start of the preset table
    # is found by searching for the name of preset #0
    preset_offset = find_strings_in_byte_stream(
        m1v2_upd_bytes, [ "Brutal Metal II", ], 0x00, 0x200, None 
    )

    presets = []
    for i in range(0,24):
        preset = ClassicPreset(m1v2_upd_bytes,preset_offset)
        amp_desc = preset["amp_id"]
        fx_desc = ",".join([ str(fx_id) for fx_id in preset["fx"]])
        print(
            f"preset {i:03}: {preset["name"]} amp={amp_desc} effects={fx_desc}"
        )
        preset_offset += len(preset.byte_stream)
        presets += [ preset ]


    # The offset into the firmware of the start of the list of 
    # DSP module names is found by searching for the name of 
    # module #100
    name_offset = find_strings_in_byte_stream(
        m1v2_upd_bytes, [ "Invalid", ], 0x80, 0x200, None 
    )
    dsp_module_names = []
    for i in range(0,89):
        name = ClassicName(m1v2_upd_bytes,name_offset)
        print(f"DSP module {i:03}: {name}")
        name_offset += len(name.byte_stream)
        
"""
    dsp_names = find_strings_in_byte_stream(
        m1v2_upd_bytes, [
            "'59 Bassman",   # id 100
            "'57 Deluxe",    # id 103
            "Princeton",     # id 106
            "'57 Champ",     # id 124
            "Studio Preamp", # id 241
            "'57 Twin",      # id 246
        ], 0, 0x100, None
    )
    for k in dsp_names:
        print(k,dsp_names[k])

"""

