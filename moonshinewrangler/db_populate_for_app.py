#! python3

import sys

from sqlite3 import Warning as Sqlite3Warning

_ALIAS_SEPARATOR=","

class AppModuleNameResolutionWarning(Sqlite3Warning):
    def __init__(self,*param_tuple):
        print("Failed to resolve app module name",file=sys.stderr)
        print("params:",param_tuple,file=sys.stderr)

def populate_product_metadata_for_app(
        cxn, xml_filename,
        # per-app constants 
        app_module_types, app_id, app_product_name_filter, 
        # per-app lambdas
        _get_root_node, 
        _get_product_nodes, _get_product_name_and_id, 
        _get_module_nodes, _get_module_name_and_id, _get_module_aliases
):
    root_node = _get_root_node(xml_filename)
    for product_node in _get_product_nodes(root_node):
        product_name, product_id = _get_product_name_and_id(product_node)
        cxn.execute(
            "INSERT INTO app_products values ( ?, ?, ?, ? )",
            (app_id, product_id, product_name, None)
        )
        if (
            app_product_name_filter is not None and 
            product_name not in app_product_name_filter
        ):
            continue
        for module_type in app_module_types:
            ((mtid,),) = cxn.execute("""
                SELECT module_type_id 
                FROM MODULE_TYPES
                WHERE aliases LIKE ?
                OR module_type_name = ?;
            """, (f"%{module_type}%", module_type,))
            for module_node in _get_module_nodes(product_node, module_type):
                module_name, app_module_id = _get_module_name_and_id(module_node)
                module_aliases = _get_module_aliases(module_node)
                # TODO: search for existing record to establish
                #       one-to-many arity between app_modules 
                #       and app_product_modules
                preexisting_records_for_module = cxn.execute("""
                    SELECT * FROM app_modules
                    WHERE module_type_id=?
                    AND app_module_id=?
                """, ( mtid, app_module_id, )).fetchall()
                if len(preexisting_records_for_module)==0:
                    cxn.execute("""                    
                        INSERT INTO app_modules (
                             module_type_id, app_module_id, app_module_name, aliases, app_id
                        ) VALUES (
                            ?, ?, ?, ?, ?
                        );
                    """, (mtid, app_module_id, module_name, module_aliases, app_id,))
                else:
                    assert len(preexisting_records_for_module)==1
                    preexisting_record_for_module = preexisting_records_for_module[0]
                    assert preexisting_record_for_module[0]==mtid
                    assert preexisting_record_for_module[1]==app_module_id
                    preexisting_name = preexisting_record_for_module[2]
                    update_name = None
                    update_aliases = None
                    extra_alias_candidate = None
                    if preexisting_name==module_name:
                        pass
                    else:
                        if module_name in preexisting_name:
                            extra_alias_candidate = module_name
                            update_name = preexisting_name
                        elif preexisting_name in module_name:
                            extra_alias_candidate = preexisting_name
                            update_name = module_name
                        else:
                            raise AppModuleNameResolutionWarning(mtid,app_module_id,module_name, ">", preexisting_record_for_module)
                    preexisting_aliases = preexisting_record_for_module[4]
                    if module_aliases in preexisting_aliases.split(_ALIAS_SEPARATOR):
                        pass
                    else:
                        update_aliases = preexisting_aliases + _ALIAS_SEPARATOR + module_aliases
                    if extra_alias_candidate is None:
                        pass
                    elif update_aliases is not None and extra_alias_candidate not in update_aliases.split(_ALIAS_SEPARATOR):
                        update_aliases = update_aliases + _ALIAS_SEPARATOR + extra_alias_candidate
                    else:
                        pass

                    if update_name is None and update_aliases is None:
                        pass
                    else:
                        if update_name is None:
                            update_name = preexisting_name
                        if update_aliases is None:
                            update_aliases = preexisting_aliases
                        cxn.execute("""                    
                            UPDATE app_modules SET 
                            app_module_name=?,
                            aliases=?
                            WHERE app_id=?
                            AND app_module_id=?
                            AND module_type_id=?
                        ;
                        """, (update_name, update_aliases, app_id, app_module_id, mtid,))
                cxn.execute("""
                    INSERT INTO app_product_modules VALUES ( 
                        ?, ?, ?, ?
                    )
                """, ( mtid, app_module_id, product_id, app_id))

