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
    for dsp_collection_index in range(0,5):
        dsp_collection = product_node[dsp_collection_index]
        assert int(dsp_collection.attrib["ID"])==dsp_collection_index, f"{dsp_collection}"
        dsp_item_type = _DSP_MODULE_TYPES[dsp_collection_index]
        for dsp_item in dsp_collection:
            dsp_item_id = int(dsp_item.attrib["ID"])
            if dsp_item_id == 0:
                continue
            assert dsp_item_id not in dsp_ids_to_types_and_names
            dsp_item_name = dsp_item.attrib["ShortName"]
            dsp_ids_to_types_and_names[dsp_item_id]=(
                dsp_item_type, dsp_item_name
            )
    generate_py_file(
        dsp_ids_to_types_and_names,
        "classic_modules",
        "FUSE_DSP_MODULES",
        lambda k,v: f"    {k:3d}: {v},\n"
    )

def generate_classic_param_db(fuse_db=_DEFAULT_FUSE_DB):
    product_node = fuse_db.getroot()
    param_names_to_types = {}
    param_types_to_values = {}
    for dsp_collection_index in range(0,5):
        dsp_collection = product_node[dsp_collection_index]
        for dsp_node in dsp_collection:
            dsp_node_id = int(dsp_node.attrib["ID"])
            for param_item in dsp_node:
                param_name = param_item.attrib["Name"]
                param_type = int(param_item.attrib["ParamType"])
                if param_name == "NULL":
                    param_pi = int(param_item.attrib["ParamIndex"])
                    param_ci = int(param_item.attrib["ControlIndex"])
                    assert param_pi==param_ci
                    param_name = f"Other_{param_pi:02d}"
                param_type_list = param_names_to_types.get(param_name,[])
                if param_type not in param_type_list:
                    param_names_to_types[param_name] = sorted(param_type_list + [param_type])
                param_value = int(param_item.text)
                type_values_and_names = param_types_to_values.get(param_type,[[],[]])
                if param_name not in type_values_and_names[0]:
                    type_values_and_names[0] += [param_name]
                    type_values_and_names[0].sort()
                if param_value not in type_values_and_names[1]:
                    type_values_and_names[1] += [param_value]
                    type_values_and_names[1].sort()
                param_types_to_values[param_type] = type_values_and_names 

    generate_py_file(
        param_names_to_types,
        "classic_param_types",
        "FUSE_PARAM_TYPES",
        lambda k,v: f'    "{k}": {v},\n'
    )

    generate_py_file(
        param_types_to_values,
        "classic_types_values",
        "FUSE_TYPE_VALUES",
        lambda k,v: f'    "{k}": (\n        {v[0]},\n        {v[1]},\n    ),\n'
    )


def generate_py_file(
        dsp_ids_to_types_and_names, 
        file_bn, dict_name, k_v_lambda
        ):
    py_file = open(f"moonshinewrangler/generated/{file_bn}.py", "wt")
    py_file.writelines([dict_name + " = {\n",])
    for k in sorted(dsp_ids_to_types_and_names):
        v = dsp_ids_to_types_and_names[k]
        py_file.writelines([k_v_lambda(k,v)])
    py_file.writelines(["}\n"])


if __name__ == "__main__":
    generate_classic_module_db()
    generate_classic_param_db()

"""    try:
        java_file= open("../maneline/maneline-lib/src/main/java/net/heretical_camelid/maneline/lib/generated/FUSE_DSP_Module.java.RSN", "wt")
        java_file.writelines([
            "package net.maneline.lib.generated;\n"
            "import net.maneline.lib.fuse.FUSE_DSP_Module;\n"
            "FUSE_DSP_MODULES = {\n",
        ])
        for k in sorted(dsp_ids_to_types_and_names):
            v = dsp_ids_to_types_and_names[k]
            java_file.writelines([f'    {k:3d}: new FUSE_DSP_Module({k},"{v[0]}","{v[1]}"),\n'])
        java_file.writelines(["}\n"])        
    except FileNotFoundError:
        pass
"""
