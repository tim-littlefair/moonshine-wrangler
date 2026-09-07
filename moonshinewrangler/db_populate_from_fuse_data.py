#! python3

from xml.dom import minidom

from db_schema_and_constants import APPS
from db_populate_for_app import populate_product_metadata_for_app

def __get_module_nodes(product_node, module_type_name):
    ( mtnode, ) = product_node.getElementsByTagName(module_type_name)
    return [
        mnode for mnode in mtnode.getElementsByTagName("Module") 
        if mnode.getAttribute("Name") != "None"
    ]

def populate_fuse_product_metadata(cxn, xml_filename):
    _FUSE_MODULE_TYPES = ( "Amplifier", "Distortion", "Modulation", "Delay", "Reverb")
    ( _FUSE_APP_ID, ) = [ k for k in APPS.keys() if APPS[k][0] == 'fender-fuse' ]
    # The schema allows modules to be tracked per product 
    # (i.e. supported physical amplifier model range), 
    # but only worrying about Mustang I/II/III/IV/V at the moment
    # TODO: Remove filter when one-to-many arity between app_modules 
    #       and app_product_modules is fixed
    _PRODUCT_NAME_FILTER = None # "Mustang I/II"
    
    _get_root_node = lambda xml_filename: minidom.parse(xml_filename)
    _get_product_nodes = lambda root_node: root_node.getElementsByTagName("Product")
    _get_module_nodes = lambda product_node, module_type_name: __get_module_nodes(product_node, module_type_name)
    _get_name_and_id = lambda node: (
        node.getAttribute("Name"),
        int(node.getAttribute("ID"))
    )
    _get_module_aliases = lambda module_node: module_node.getAttribute("ShortName")
    populate_product_metadata_for_app(
        cxn, xml_filename, 
        _FUSE_MODULE_TYPES, _FUSE_APP_ID, _PRODUCT_NAME_FILTER, 
        _get_root_node, _get_product_nodes, _get_name_and_id, 
        _get_module_nodes, _get_name_and_id, _get_module_aliases
    )

