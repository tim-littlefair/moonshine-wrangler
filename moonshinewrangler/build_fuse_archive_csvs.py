#! python3

import os
import sys
import traceback

from xml.dom import minidom

_PRESET_DICT = {}
_AMP_DICT = {}
_SC_DICT = {}


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
    sc_types, sc_ids = effects_sequence(root_node)
    preset_record = ( amp_name, amp_id, preset_name, author, sc_types, sc_ids)
    _PRESET_DICT[fname] = preset_record
    amp_key = (amp_id,amp_name)
    if amp_key in _AMP_DICT:
        _AMP_DICT[amp_key][fname] = preset_record
    else:
        _AMP_DICT[amp_key] = { fname: preset_record }
    if sc_types in _SC_DICT:
        _SC_DICT[sc_types][fname] = preset_record
    else: 
        _SC_DICT[sc_types] = { fname: preset_record}

def summarize_by_amp():
    for k in sorted(_AMP_DICT.keys()):
        print(f"{k},{len(_AMP_DICT[k]),(sorted(_AMP_DICT[k].keys())[0])}")

def summarize_by_sctypes():
    for k in sorted(_SC_DICT.keys()):
        print(f"{k},{len(_SC_DICT[k]),(sorted(_SC_DICT[k].keys())[0])}")


def effects_sequence(root_node):
    fx_node_names = ( "Stompbox","Modulation","Delay","Reverb")
    # 'pti' stands for pos, type and id
    fx_pti_array  = [
        (
            int(fx_module_node.getAttribute("POS")),
            fx_module_node.parentNode.tagName[0],
            int(fx_module_node.getAttribute("ID")),
        )
        for fx_module_node in root_node.getElementsByTagName("Module")
    ]
    sigchain_types = ""
    sigchain_ids = []
    for pti_item in sorted(fx_pti_array[1:]):
        # POS values 0-4 signify before amp, 5-infinity signify after amp,
        # so we need to insert the amp details in pti_item[0] after
        # any effects with low values of POS
        if "A" in sigchain_types:
            pass
        elif pti_item[0]>4:
            # insert the amp
            sigchain_ids += [ fx_pti_array[0][2] ]
            sigchain_types += "A"
        else:
            pass
        if pti_item[2]==0:
            # lower case signifies that the slot is empty
            # sigchain_types += pti_item[1].lower()
            pass
        else:
            sigchain_ids += [ pti_item[2] ]
            sigchain_types += pti_item[1]
    if "A" not in sigchain_types:
        sigchain_ids += [ fx_pti_array[0][2] ]
        sigchain_types += "A"
    return sigchain_types, sigchain_ids




    

if __name__ == "__main__":
    dir = "_work/fuse_archive"
    for f in os.listdir(dir):
        if f.endswith(".fuse") is False:
            continue
        try:
            process_fuse_file(dir,f)
        except:
            print(f"processing {f}")
            traceback.print_exc(3)
            break
    summarize_by_amp()
    summarize_by_sctypes()