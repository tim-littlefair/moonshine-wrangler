#! python3

import os
import sys
import traceback

from xml.dom import minidom

_PRESET_DICT = {}
_AMP_DICT = {}

def process_fuse_file(dir, fname):
    path = os.path.join(dir,fname)
    xml_text = open(path,encoding="ISO-8859-1").read()
    if xml_text[0] != "<":
        # Some files start with a byte order mark, which 
        # Expat/minidom don't like
        xml_text = xml_text[3:]
    ( root_node, ) = minidom.parseString(xml_text).getElementsByTagName("Preset")
    amp_name = root_node.getAttribute("amplifier")
    amp_id = int(root_node.getAttribute("ProductId"))
    ( info_node, ) = root_node.getElementsByTagName("Info")
    preset_name = info_node.getAttribute("name")
    author = info_node.getAttribute("author")
    preset_record = ( amp_name, amp_id, preset_name, author)
    _PRESET_DICT[fname] = preset_record
    amp_key = (amp_id,amp_name)
    if amp_key in _AMP_DICT:
        _AMP_DICT[amp_key][fname] = preset_record
    else:
        _AMP_DICT[amp_key] = { fname: preset_record }

def summarize_by_amp():
    for k in sorted(_AMP_DICT.keys()):
        print(f"{k},{len(_AMP_DICT[k])}")

if __name__ == "__main__":
    dir = "_work/fuse_archive"
    for f in os.listdir(dir):
        if f.endswith(".fuse") is False:
            continue
        try:
            process_fuse_file(dir,f)
        except:
            print(f"processing {f}")
            traceback.print_exc(0)
    summarize_by_amp()