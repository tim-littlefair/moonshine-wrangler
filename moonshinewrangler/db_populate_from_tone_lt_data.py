#! python3

import json
import os

from db_schema_and_constants import APPS
from db_populate_for_app import populate_product_metadata_for_app

_EXTRACTED_LT_DATA_DIR = None
_MODULE_NAME_WITHOUT_PREFIX = "_name_without_prefix"
_MODULE_TYPE_NAME = "_module_type_name"
_ALIAS_FROM_ML = "_alias_from_module_list"

_missing_modules = []


def _lt_json_objects(fname_prefix):
    matching_paths = [
        os.path.join(_EXTRACTED_LT_DATA_DIR,fname)
        for fname in os.listdir(_EXTRACTED_LT_DATA_DIR)
        if (
            fname.startswith(fname_prefix) and
            fname.endswith(".json")
        )
    ]
    return [ json.load(open(path)) for path in matching_paths ]

def __get_module_nodes(product_node, module_type_name):
    global _missing_modules
    product_name = product_node[1]
    ( product_modules, ) = _lt_json_objects(f"module_list-{product_name}-")
    dspunits_for_type = None
    if( 
        (product_name == "mustang" and module_type_name == "eq") or
        (product_name == "rumble" and module_type_name == "reverb")
    ):
        # rumble has no 'reverb' modules, mustang has no 'eq' modules
        return []
    elif module_type_name == "amp":
            dspunits_for_type = product_modules[module_type_name]["dspUnits"]        
    else:
        ( dspunits_for_type, ) =  [
            ec["dspUnits"]
            for ec in product_modules["effectCategories"]
            if ec["categoryName"] == module_type_name 
        ]
    product_modules = []
    for du in dspunits_for_type:
        trimmed_module_name = du["FenderId"].replace("DUBS_","").replace("Mustang","").replace("Reverb","")
        module_type_fname_prefix = module_type_name
        # Rumble LT25 has a single 'eq' (equalizer) module instead of 'reverb' 
        # but jams a couple of 'reverb' modules into the 'delay' category
        if product_name!="rumble":
            pass
        elif du["FenderId"].endswith("Reverb"):
            module_type_fname_prefix = module_type_fname_prefix.replace("delay","reverb")
        else:
            module_type_fname_prefix = module_type_fname_prefix.replace("eq","filter")
        candidate_module_dicts = _lt_json_objects(f"{module_type_fname_prefix}-{trimmed_module_name}")
        if len(candidate_module_dicts)>0:
            pass
        elif trimmed_module_name == "Passthru":
            continue
        else:
            _missing_modules += [ (product_name,module_type_name,du["FenderId"],), ]
            continue
        candidate_module_dicts[0][_MODULE_NAME_WITHOUT_PREFIX] = trimmed_module_name
        candidate_module_dicts[0][_MODULE_TYPE_NAME] = module_type_name
        candidate_module_dicts[0][_ALIAS_FROM_ML] = du["menuName18Max"]
        product_modules += [ candidate_module_dicts[0] ]
    return  product_modules

_next_lt_module_id = 7101
_LT_MODULE_NAMES_TO_TYPES_AND_IDS = {}
def __get_module_name_and_id(module_node):
    global _next_lt_module_id
    lt_module_key = ( 
        module_node[_MODULE_TYPE_NAME], 
        module_node[_MODULE_NAME_WITHOUT_PREFIX]
    )
    if  lt_module_key not in _LT_MODULE_NAMES_TO_TYPES_AND_IDS.keys():
        _LT_MODULE_NAMES_TO_TYPES_AND_IDS[lt_module_key] = _next_lt_module_id
        _next_lt_module_id +=1
    return (lt_module_key[1], _LT_MODULE_NAMES_TO_TYPES_AND_IDS[lt_module_key])
    
def populate_tone_lt_product_metadata(cxn, extracted_json_dir):
    global _EXTRACTED_LT_DATA_DIR
    _EXTRACTED_LT_DATA_DIR = extracted_json_dir
    _TONE_LT_MODULE_TYPES = ( "amp", "stomp", "mod", "delay", "reverb", "eq", )
    ( _TONE_LT_APP_ID, ) = [ k for k in APPS.keys() if APPS[k][0] == 'fender-tone-lt' ]
    _PRODUCT_NAME_FILTER = None

    # The extracted data from the LT installer consists of many
    # documents, the root 'node' is the directory which contains 
    # them
    _get_root_node = lambda source_path: extracted_json_dir

    # The Fender Tone LT Desktop app supports Mustang and Rumble devices.
    # There are 3 Mustang LT models, but they share a single list of 
    # modules extracted from the app installer.
    _get_product_nodes = lambda root_node: ( (6101, "mustang"), (6102, "rumble") )
    _get_product_name_and_id = lambda product_node: product_node

    _get_module_nodes = lambda product_node, module_type_name: __get_module_nodes(product_node, module_type_name)
    _get_module_name_and_id = lambda module_node: __get_module_name_and_id(module_node)
    _get_module_aliases = lambda module_node: module_node[_ALIAS_FROM_ML]
    populate_product_metadata_for_app(
        cxn, extracted_json_dir, 
        _TONE_LT_MODULE_TYPES, _TONE_LT_APP_ID, _PRODUCT_NAME_FILTER, 
        _get_root_node, _get_product_nodes, _get_product_name_and_id, 
        _get_module_nodes, _get_module_name_and_id, _get_module_aliases
    )
    for mm in _missing_modules:
        print(mm)



