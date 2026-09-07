#! python3

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
                    cur = cxn.execute("""                    
                        INSERT INTO app_modules (
                             module_type_id, app_module_id, app_module_name, aliases, app_id
                        ) VALUES (
                            ?, ?, ?, ?, ?
                        );
                    """, (mtid, app_module_id, module_name, module_aliases, app_id,))
                    # the primary key of app_modules is created by AUTOINCREMENT
                    # so we get it from the cursor
                    app_module_id = cur.lastrowid
                    cxn.execute("""
                        INSERT INTO app_product_modules VALUES ( 
                            ?, ?, ?, ?
                        )
                    """, ( mtid, app_module_id, product_id, app_id))
                else:
                    assert len(preexisting_records_for_module)==1
                    preexisting_record_for_module = preexisting_records_for_module[0]
                    print(mtid,app_module_id,module_name, ">", preexisting_record_for_module)
                    assert preexisting_record_for_module[0]==mtid
                    assert preexisting_record_for_module[1]==app_module_id
                    #assert preexisting_record_for_module[2]==module_name

