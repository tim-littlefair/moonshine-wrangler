#! python3

import os
import time

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

def populate_constant_tables(cxn):
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

