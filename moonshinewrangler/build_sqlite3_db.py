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
            PRIMARY KEY(module_type_id)
        );
        CREATE TABLE app_modules (
            app_module_id INTEGER NOT NULL,
            app_module_type_id INTEGER NOT NULL,
            app_id INTEGER NOT NULL,
            app_module_name TEXT NOT NULL,
            PRIMARY KEY(app_module_id),
            FOREIGN KEY(app_module_type_id) REFERENCES app_module_types,
            FOREIGN KEY(app_id) REFERENCES apps 
        )
    """

APPS = { 
    0: 'mw-app-neutral', 
    1: 'fender-fuse', 
    2: 'fender-tone-lt', 
    3: 'fender-tone-mobile' 
}

MODULE_TYPES = { 
    0: 'mw-unnassigned', 
    1: 'amp', 
    2: 'stomp', 
    3: 'mod', 
    4: 'delay', 
    5: 'reverb', 
    6: 'eq', 
    7: 'utility' 
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
                {k}, "{APPS[k]}"
            )
        """)
    for k in sorted(MODULE_TYPES.keys()):
        cxn.execute(f"""
            INSERT INTO MODULE_TYPES VALUES (
                {k}, "{MODULE_TYPES[k]}"
            )
        """)

def dump(cxn):
    for tbl in ( "apps", "module_types"):
        print(f"{tbl}:")
        for row in cxn.execute(f"SELECT * FROM {tbl};"):
            print(row)

if __name__ == "__main__":
    if os.path.exists(_DB_DIR) is False:
        os.mkdir(_DB_DIR)
    cxn = create_db_schema()
    populate_metadata(cxn)
    dump(cxn)

