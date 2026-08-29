#! python3

from xml.dom import minidom

from db_schema_and_constants import APPS
from db_populate_for_app import populate_product_metadata_for_app

def populate_tone_lt_product_metadata(cxn, json_filename):
    _TONE_LT_MODULE_TYPES = ( )
    ( _TONE_LT_APP_ID, ) = [ k for k in APPS.keys() if APPS[k][0] == 'fender-tone-lt' ]
    _PRODUCT_NAME_FILTER = None
    _get_root_node = lambda json_filename: None
    _get_product_nodes = lambda root_node: ()
    _get_node_name_and_id = lambda module_node: (None, None, )
    _get_module_nodes = lambda product_node: ()
    _get_node_name = lambda module_node: None
    populate_product_metadata_for_app(
        cxn, json_filename, 
        _TONE_LT_MODULE_TYPES, _TONE_LT_APP_ID, _PRODUCT_NAME_FILTER, 
        _get_root_node, _get_product_nodes, _get_node_name_and_id, _get_module_nodes, _get_node_name
    )

