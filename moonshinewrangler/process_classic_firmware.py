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

import zipfile
import binascii

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
    byte_stream, target_strings, bytes_before, buffer_length, string_offsets=[]
):
    retval = {}
    targets_found = []
    for s in target_strings:
        s_bytes = s.encode("utf-8")
        offset = 0
        while True:
            offset = byte_stream.find(s_bytes, offset+1)
            if offset == -1:
                break
            buffer = byte_stream[
                offset-bytes_before:
                offset-bytes_before+buffer_length
            ]
            buffer_hex = str(binascii.b2a_hex(buffer),"utf-8")
            string_items = { }
            end_offset = offset + buffer_length
            found_line = "\n".join(
                [f"{offset:08x} {s:20s}"] + 
                [f"{buffer_hex[n*32:(n+1)*32]}" for n in range(0,7)] +
                [f"{end_offset:08x}"]
            )
            print(found_line)
            retval[s]=ClassicPreset(buffer)
    return retval

def null_terminated_string(byte_string):
    first_nul_pos = byte_string.find(0)
    if first_nul_pos!=-1:
        byte_string = byte_string[0:first_nul_pos]
    return str(byte_string,"utf-8")

class ClassicPreset(dict):
    def __init__(self, byte_stream):
        self.byte_stream = byte_stream
        self["name"]=null_terminated_string(self.byte_stream[0:20])
        self["amp_id"]=self.byte_stream[20]
        self["fx"] = [ self.byte_stream[44+(slot*18)] for slot in range(0,4)]

    def effect_id(self,slot):
        return byte_stream[44+(slot*18)]
    

if __name__ == "__main__":
    m1v2_upd_bytes = get_upd_stream("_work/reference_files/V2_Mustang1_2.2.zip")
    print(len(m1v2_upd_bytes))
    presets = find_strings_in_byte_stream(
        m1v2_upd_bytes, [
            "Brutal Metal II", 
            "Super-Live Album", 
            "Liquid Solo", 
            "American90sChorus", 
            "Pigs Can Fly", 
            "Chimey Deluxe"
        ], 0, 0x78
    )
    for k in presets.keys():
        print(presets[k])
    


