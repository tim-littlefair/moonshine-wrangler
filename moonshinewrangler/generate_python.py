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
    product_node = fuse_db.getroot()
    dsp_ids_to_types_and_names = {}
    amplifier_dsp_ids_to_types_and_names = {}
    effect_dsp_ids_to_types_and_names = {}
    for dsp_collection_index in range(0,5):
        dsp_collection = product_node[dsp_collection_index]
        assert int(dsp_collection.attrib["ID"])==dsp_collection_index, f"{dsp_collection}"
        dsp_item_type = _DSP_MODULE_TYPES[dsp_collection_index]
        if True:
            pass
        elif dsp_collection_index==0:
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

    py_file = open("moonshinewrangler/generated/classic_modules.py", "wt")
    py_file.writelines([
        "FUSE_DSP_MODULES = {\n",])
    for k in sorted(dsp_ids_to_types_and_names):
        v = dsp_ids_to_types_and_names[k]
        py_file.writelines([f"    {k:3d}: {v},\n"])
    py_file.writelines(["}\n"])

    try:
        java_file= open("../maneline/maneline-lib/src/main/java/net/heretical_camelid/maneline/lib/generated/FUSE_DSP_Module.java.RSN", "wt")
        java_file.writelines([
            "package net.maneline.lib.generated;\n"
            "import net.maneline.lib.fuse.FUSE_DSP_Module;\n"
            "FUSE_DSP_MODULES = {\n",
        ])
        for k in sorted(dsp_ids_to_types_and_names):
            v = dsp_ids_to_types_and_names[k]
            java_file.writelines([f'    {k:3d}: new FUSE_DSP_Module({k},{v[0]},"{v[1]}"),\n'])
        java_file.writelines(["}\n"])        
    except FileNotFoundError:
        pass

if __name__ == "__main__":
    generate_classic_module_db()