#! python3

from xml.dom import minidom

from db_schema_and_constants import APPS

def populate_fuse_product_metadata(cxn, xml_filename):
    _FUSE_MODULE_TYPES = ( "Amplifier", "Distortion", "Modulation", "Delay", "Reverb")
    ( _FUSE_APP_ID, ) = [ k for k in APPS.keys() if APPS[k][0] == 'fender-fuse' ]
    # The schema allows modules to be tracked per product 
    # (i.e. supported physical amplifier model range), 
    # but only worrying about Mustang I/II/III/IV/V at the moment
    # TODO: Remove filter when one-to-many arity between app_modules 
    #       and app_product_modules is fixed
    _PRODUCT_NAME_FILTER = "Mustang I/II"
    _get_root_node = lambda xml_filename: minidom.parse(xml_filename)
    _get_product_nodes = lambda root_node: root_node.getElementsByTagName("Product")
    _get_node_name_and_id = lambda module_node: (
        module_node.getAttribute("Name"),
        module_node.getAttribute("ID"),
    )
    _get_module_nodes = lambda product_node: product_node.getElementsByTagName("Module") 
    _get_node_name = lambda module_node: module_node.getAttribute("Name")
    populate_product_metadata_for_app(
        cxn, xml_filename, 
        _FUSE_MODULE_TYPES, _FUSE_APP_ID, _PRODUCT_NAME_FILTER, 
        _get_root_node, _get_product_nodes, _get_node_name_and_id, _get_module_nodes, _get_node_name
    )

def populate_product_metadata_for_app(
        cxn, xml_filename,
        # per-app constants 
        app_module_types, app_id, app_product_name_filter, 
        # per-app lambdas
        _get_root_node, _get_product_nodes, _get_node_name_and_id, _get_module_nodes, _get_node_name
):
    root_node = _get_root_node(xml_filename)
    for product_node in _get_product_nodes(root_node):
        product_name, product_id = _get_node_name_and_id(product_node)
        if (
            app_product_name_filter is not None and 
            product_name not in app_product_name_filter
        ):
            continue
        cxn.execute(
            "INSERT INTO app_products values ( ?, ?, ? )",
            (app_id, product_id, product_name,)
        )
        for module_type in app_module_types:
            ((mtid,),) = cxn.execute("""
                SELECT module_type_id 
                FROM MODULE_TYPES
                WHERE aliases LIKE ?
                OR module_type_name = ?;
            """, (f"%{module_type}%", module_type,))
            for module_node in _get_module_nodes(product_node):
                module_name = _get_node_name(module_node)
                # TODO: search for existing record to establish
                #       one-to-many arity between app_modules 
                #       and app_product_modules
                cxn.execute("""                    
                    INSERT INTO app_modules (
                        app_module_name, app_id, module_type_id
                    ) VALUES (
                        ?, ?, ?
                    );
                """, (module_name, app_id, mtid,))
                # the primary key of app_modules is created by AUTOINCREMENT
                # so we get it from the table
                ((app_module_id,),) = cxn.execute("SELECT MAX(app_module_id) FROM app_modules")
                cxn.execute("""
                    INSERT INTO app_product_modules VALUES ( 
                        ?, ?, ?
                    )
                """, ( app_module_id, product_id, app_id))

