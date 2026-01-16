#! python3

# Author: Tim Littlefair, 2026-
# The author licenses this progress to you under the MIT License
# See the file LICENSE in the base directory of the distribution for 
# full terms of this license.

import json
import os
import sys
import xml.etree.ElementTree as ET

_DEFAULT_FUSE_DB=None
_default_fuse_db_filename="./_work/fuse_data/product13-Mustang_V2_I+II.xml"

_DEFAULT_TONE_LT_DIR="./_work/tone_mustang_lt_data"

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
    param_types_to_names_and_values = {}
    module_params = {}
    for dsp_collection_index in range(0,5):
        dsp_collection = product_node[dsp_collection_index]
        for dsp_node in dsp_collection:
            dsp_node_id = int(dsp_node.attrib["ID"])
            for param_item in dsp_node:
                param_pi = int(param_item.attrib["ParamIndex"])
                param_ci = int(param_item.attrib["ControlIndex"])
                param_name = param_item.attrib["Name"]
                param_type = int(param_item.attrib["ParamType"])
                if param_name == "NULL":
                    assert param_pi==param_ci
                    param_name = f"Other_{param_pi:02d}"
                param_type_list = param_names_to_types.get(param_name,[])
                if param_type not in param_type_list:
                    param_names_to_types[param_name] = sorted(param_type_list + [param_type])
                param_value = int(param_item.text)
                type_names_and_values = param_types_to_names_and_values.get(param_type,[[],[]])
                if param_name not in type_names_and_values[0]:
                    type_names_and_values[0] += [param_name]
                    type_names_and_values[0].sort()
                if param_value not in type_names_and_values[1]:
                    type_names_and_values[1] += [param_value]
                    type_names_and_values[1].sort()
                param_types_to_names_and_values[param_type] = type_names_and_values
                mp_key = ( param_pi, param_name, param_type, )
                mp_module_list = module_params.get(mp_key, [])
                module_params[mp_key] = sorted(mp_module_list + [ dsp_node_id ])
    generate_py_file(
        param_names_to_types,
        "classic_param_types",
        "FUSE_PARAM_TYPES",
        lambda k,v: f'    "{k}": {v},\n'
    )

    generate_py_file(
        param_types_to_names_and_values,
        "classic_types_values",
        "FUSE_TYPE_VALUES",
        lambda k,v: f'    "{k}": (\n        {v[0]},\n        {v[1]},\n    ),\n'
    )
    
    generate_py_file(
        module_params,
        "classic_module_params",
        "FUSE_MODULE_PARAMS",
        lambda k,v: f'    {k}: {v},\n'
    )

def generate_tone_lt_param_db(data_dir=_DEFAULT_TONE_LT_DIR, module_types=None):
    if module_types is None:
        module_types = ( 
            "amp", "stomp", "mod", "delay", "reverb", 
            "filter", "dynamics", "utility"
        )
        tone_lt_module_params = {}
        for f in os.listdir(data_dir):
            if f.endswith(".json")==False:
                continue
            module = json.load(open(os.path.join(data_dir,f)))
            try :
                if module["info"]["subcategory"] not in module_types:
                    continue
            except KeyError:
                continue
            module_id = module["FenderId"]
            for param_entry in module["ui"]["uiParameters"]:
                param_id = param_entry["controlId"]
                param_key = ( module_id, param_id )
                control_type = param_entry["controlType"]
                param_details = tone_lt_module_params.get(param_key, None)
                this_entry_values = [ control_type ]
                try:
                    if control_type == "continuous":
                        this_entry_values += [
                            param_entry["max"],
                            param_entry["min"],
                            param_entry["numTicks"],
                        ]
                        if "remap" in param_entry:
                            this_entry_values += [
                                param_entry["remap"]["max"],
                                param_entry["remap"]["min"],
                            ]
                        if "taper" in param_entry:
                            this_entry_values += [ param_entry["taper"] ]
                    else:
                        this_entry_values += [ param_entry["listItems"] ]
                    assert param_details is None or param_details==this_entry_values
                    tone_lt_module_params[param_key] = this_entry_values
                except KeyError:
                    print(f"KeyError raised while processing: {f}")
                    print("Entry: " + str(param_entry))
                except AssertionError:
                    print(f"AssertionError raised while processing: {f}")
                    print("Entry: " + str(param_entry))  
                    print("New params: " + str(this_entry_values)) 
                    print("Previous: " + str(param_details))                 
    generate_py_file(
        tone_lt_module_params,
        "tone_lt_module_params",
        "TONE_LT_MODULE_PARAMS",
        lambda k,v: f'    {k}: {v},\n'
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
    generate_tone_lt_param_db()

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
