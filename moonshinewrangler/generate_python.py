#! python3

# Author: Tim Littlefair, 2026-
# The author licenses this progress to you under the MIT License
# See the file LICENSE in the base directory of the distribution for 
# full terms of this license.

import sys
import xml.etree.ElementTree as ET

_DEFAULT_FUSE_DB=None
_default_fuse_db_filename="./_work/fuse_data/product13-Mustang_V2_I+II.xml"
try:
    _DEFAULT_FUSE_DB = ET.parse(_default_fuse_db_filename)
except FileNotFoundError:
    print("\n".join([
        f"{_default_fuse_db_filename} not found.",
        "Run 'python3 ./moonshinewrangler/process_fuse_installer.py",
        "before attempting to run this script"
    ]), file=sys.stderr)
    sys.exit(1)

# The FenderFUSE serialization format and associated metadata contain
# information on 5 different types of DSP modules identified as 
# Amplifier, Distortion, Modulation, Delay and Reverb.
# The later FenderTONE LT Desktop and mobile apps use the 
# term 'Stomp' instead of 'Distortion'.  It is convenient to 
# adopt the 'Stomp' term here, so that the first letters of 
# each type can be used as an abbreviation to identify the module 
# type.
_DSP_MODULE_TYPES = "ASMDR"
                            
def generate_classic_module_db(fuse_db=_DEFAULT_FUSE_DB):
    py_file = open("moonshinewrangler/generated/classic_modules.py", "wt")
    product_node = fuse_db.getroot()
    amplifier_dsp_ids_to_types_and_names = {}
    effect_dsp_ids_to_types_and_names = {}
    for dsp_collection_index in range(0,5):
        dsp_collection = product_node[dsp_collection_index]
        assert int(dsp_collection.attrib["ID"])==dsp_collection_index, f"{dsp_collection}"
        dsp_item_type = _DSP_MODULE_TYPES[dsp_collection_index]
        dsp_ids_to_types_and_names = None
        if dsp_collection_index==0:
            dsp_ids_to_types_and_names=amplifier_dsp_ids_to_types_and_names
        else:
            dsp_ids_to_types_and_names=effect_dsp_ids_to_types_and_names
        for dsp_item in dsp_collection:
            dsp_item_id = int(dsp_item.attrib["ID"])
            if dsp_item_id == 0:
                continue
            assert dsp_item_id not in dsp_ids_to_types_and_names
            dsp_item_name = dsp_item.attrib["ShortName"]
            dsp_ids_to_types_and_names[dsp_item_id]=(
                dsp_item_type, dsp_item_name
            )
    # Children of this node represent DSP units which simulate specific amplifier models
    py_file.writelines([
        "MODULE_NAMES = {\n",
        "    # Amplifiers\n",
    ])
    for k in sorted(amplifier_dsp_ids_to_types_and_names):
        v = amplifier_dsp_ids_to_types_and_names[k]
        py_file.writelines([f"    {k:3d}: {v},\n"])
    py_file.writelines(["    # Effects\n"])
    for k in sorted(effect_dsp_ids_to_types_and_names):
        v = effect_dsp_ids_to_types_and_names[k]
        py_file.writelines([f"    {k:3d}: {v},\n"])
    py_file.writelines(["}\n"])


if __name__ == "__main__":
    generate_classic_module_db()