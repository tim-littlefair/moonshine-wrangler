#! python3

import os
import time
import traceback
from xml.dom import minidom

import sqlite3

_DB_SCHEMA = """
    CREATE TABLE apps (
        app_id INTEGER NOT NULL,
        app_name TEXT NOT NULL,
        PRIMARY KEY(app_id)
    );
    CREATE TABLE module_types (
        module_type_id INTEGER NOT NULL,
        module_type_name TEXT NOT NULL,
        aliases TEXT,
        PRIMARY KEY(module_type_id)
    );
    CREATE TABLE app_products (
        app_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        PRIMARY KEY (app_id, product_id),
        FOREIGN KEY (app_id) REFERENCES apps
    );
    CREATE TABLE app_modules (
        app_module_id INTEGER NOT NULL,
        app_module_name TEXT NOT NULL,
        app_id INTEGER NOT NULL,
        module_type_id INTEGER NOT NULL,
        PRIMARY KEY(app_module_id AUTOINCREMENT),
        FOREIGN KEY(module_type_id) REFERENCES module_types,
        FOREIGN KEY(app_id) REFERENCES apps 
    );
-- " ""

-- s = "" "
    CREATE TABLE app_product_modules (
        product_id INTEGER NOT NULL,
        app_module_id INTEGER NOT NULL,
        -- app_id could be accessed via app_module, but is also 
        -- included in this table so that we can constrain product_id
        -- using a lookup into app_products
        app_id INTEGER NOT NULL,
        PRIMARY KEY (product_id, app_module_id),
        FOREIGN KEY (app_id, product_id) REFERENCES app_products
        FOREIGN KEY (app_module_id) REFERENCES app_modules
    );
"""

APPS = { 
    0: ('mw-app-neutral',), 
    1: ('fender-fuse',),
    2: ('fender-tone-lt',), 
    3: ('fender-tone-mobile',), 
}

MODULE_TYPES = { 
    0: ('amp', 'Amplifier'),
    1: ('stomp', 'Distortion'),
    2: ('mod', 'Modulation'),
    3: ('delay', 'Delay'),
    4: ('reverb', 'Reverb'),
    5: ('eq', None),
    6: ('utility', None),
}

_DB_DIR = "_work/sqlite3_db"
_db_path = None


def create_db_schema(dbname=None):
    if dbname is None:
        dbname = f"mw-{int(time.time())}.db"
    global _db_path
    _db_path = os.path.join(_DB_DIR,dbname)
    cxn = sqlite3.connect(_db_path)
    cur = cxn.cursor()
    cur.executescript(_DB_SCHEMA)
    return cxn

def populate_metadata(cxn):
    for k in sorted(APPS.keys()):
        cxn.execute(f"""
            INSERT INTO APPS VALUES (
                {k}, ?
            )
        """, APPS[k])
    for k in sorted(MODULE_TYPES.keys()):
        cxn.execute(f"""
            INSERT INTO module_types VALUES (
                {k}, ?, ?
            )
        """, MODULE_TYPES[k])

def populate_fuse_product_metadata(cxn, xml_filename):
    _FUSE_MODULE_TYPES = ( "Amplifier", "Distortion", "Modulation", "Delay", "Reverb")
    ( _FUSE_APP_ID, ) = [ k for k in APPS.keys() if APPS[k][0] == 'fender-fuse' ]
    document = minidom.parse(xml_filename)
    for product_node in document.getElementsByTagName("Product"):
        product_name = product_node.getAttribute("Name")
        product_id = product_node.getAttribute("ID")
        # The schema allows modules to be tracked per product 
        # (i.e. supported physical amplifier model range), 
        # but only worrying about Mustang I/II/III/IV/V at the moment
        if product_name != "Mustang I/II":
            continue
        cxn.execute(
            "INSERT INTO app_products values ( ?, ?, ? )",
            (_FUSE_APP_ID, product_id, product_name,)
        )
        for module_type in _FUSE_MODULE_TYPES:
            ((mtid,),) = cxn.execute("""
                SELECT module_type_id 
                FROM MODULE_TYPES
                WHERE aliases LIKE ?
                OR module_type_name = ?;
            """, (f"%{module_type}%", module_type,))
            for module_node in product_node.getElementsByTagName("Module"):
                module_name = module_node.getAttribute("Name")
                cxn.execute("""                    
                    INSERT INTO app_modules (
                        app_module_name, app_id, module_type_id
                    ) VALUES (
                        ?, ?, ?
                    );
                """, (module_name, _FUSE_APP_ID, mtid,))
                # the primary key of app_modules is created by AUTOINCREMENT
                # so we get it from the table
                ((app_module_id,),) = cxn.execute("SELECT MAX(app_module_id) FROM app_modules")
                cxn.execute("""
                    INSERT INTO app_product_modules VALUES ( 
                        ?, ?, ?
                    )
                """, ( app_module_id, product_id, _FUSE_APP_ID))

def dump(cxn):
    for tbl in ( "apps", "app_products", "module_types", "app_modules", "app_product_modules" ):
        print(f"{tbl}:")
        for row in cxn.execute(f"SELECT * FROM {tbl};"):
            print(row)

if __name__ == "__main__":
    if os.path.exists(_DB_DIR) is False:
        os.mkdir(_DB_DIR)
    cxn = create_db_schema()
    try:
        populate_metadata(cxn)
        cxn.commit()
        populate_fuse_product_metadata(cxn,"_work/fuse_data/all_products.xml")
        dump(cxn)
    except:
        traceback.print_exc()
        dump(cxn)

