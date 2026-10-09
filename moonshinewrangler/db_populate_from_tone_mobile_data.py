#! python3

import json
import os
from xml.dom import minidom

from db_schema_and_constants import APPS
from db_populate_for_app import populate_product_metadata_for_app


def populate_tone_mobile_product_metadata(cxn, extracted_json_dir):
    _TONE_MOBILE_MODULE_TYPES = ( "amp", "stomp", "mod", "delay", "reverb", "eq", )
    ( _TONE_MOBILE_APP_ID, ) = [ k for k in APPS.keys() if APPS[k][0] == 'fender-tone-mobile' ]
    _PRODUCT_NAME_FILTER = None
    _get_root_node = lambda json_filename: None
    _get_product_nodes = lambda root_node: ( 
        # The Fender Tone LT Mobile app supports Mustang GT, GTX, LTX and 
        # Mustang Micro Plus models and also two non-LT Rumble models
        (6201, "mustang-gt"),  # Mustang GT40, GT100, GT200; released around 2016
        (6202, "rumble"),      # Rumble Studio 40, Stage 800; released around 2016
        (6203, "mustang-gtx"), # Mustang GTX50, GTX100; released around 2020
        (6204, "mmp"),         # Mustang Micro Plus; released 2024
        (6205, "mustang-ltx"), # Mustang LTX50, LTX100; released 2025
    )
    _get_product_name_and_id = lambda product_node: product_node
    _get_module_nodes = lambda product_node, module_type_name: __get_module_nodes(product_node, module_type_name)
    _get_module_name_and_id = lambda module_node: __get_module_name_and_id(module_node)
    _get_module_aliases = lambda module_node: module_node[_ALIAS_FROM_ML]
    populate_product_metadata_for_app(
        cxn, extracted_json_dir, 
        _TONE_MOBILE_MODULE_TYPES, _TONE_MOBILE_APP_ID, _PRODUCT_NAME_FILTER, 
        _get_root_node, _get_product_nodes, _get_product_name_and_id,
         _get_module_nodes, _get_module_name_and_id, _get_module_aliases
    )

_EXTRACTED_MOBILE_DATA_DIR = "_work/tone_mobile_data"
_MODULE_NAME_WITHOUT_PREFIX = "_name_without_prefix"
_MODULE_TYPE_NAME = "_module_type_name"
_ALIAS_FROM_ML = "_alias_from_module_list"

def __get_module_nodes(product_node, module_type_name):
    global _missing_modules
    product_name = product_node[1]
    product_modules = None
    if product_name == "mustang-gtx":
        ( product_modules, ) = _mobile_json_objects(f"productFamily-gtx")
    elif product_name == "rumble":
        ( product_modules, ) = _mobile_json_objects(f"productFamily-rumble")
    else:
        ( product_modules, ) = _mobile_json_objects(f"productFamily-mustang")
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
        try:
            ( dspunits_for_type, ) =  [
                ec["dspUnits"]
                for ec in product_modules["effectCategories"]
                if ec["categoryName"] == module_type_name 
            ]
        except ValueError:
            return []
    product_modules = []
    for du in dspunits_for_type:
        merged_modules = {}
        trimmed_module_name = du["FenderId"].replace("DUBS_","").replace("ACD_","").replace("Mustang","").replace("Reverb","")
        merged_modules[_MODULE_NAME_WITHOUT_PREFIX] = trimmed_module_name
        merged_modules[_MODULE_TYPE_NAME] = module_type_name
        merged_modules[_ALIAS_FROM_ML] = du["menuName18Max"]
        product_modules += [ merged_modules ]
    return product_modules


_next_lt_module_id = 7201
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


def _mobile_json_objects(fname_prefix):
    matching_paths = [
        os.path.join(_EXTRACTED_MOBILE_DATA_DIR,fname_prefix) + ".json"
    ]
    return [ json.load(open(path)) for path in matching_paths ]