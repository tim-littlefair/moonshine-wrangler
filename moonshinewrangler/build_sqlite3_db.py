#! python3

import os
import traceback

from db_schema_and_constants import APPS, create_db_schema, populate_constant_tables, _DB_DIR
from db_populate_from_fuse_data import populate_fuse_product_metadata
from db_populate_from_tone_lt_data import populate_tone_lt_product_metadata
from db_populate_from_tone_mobile_data import populate_tone_mobile_product_metadata

def dump(cxn):
    for tbl in ( 
        # "apps", "app_products", "module_types", 
        "app_modules", 
        # "app_product_modules" 
    ):
        print(f"{tbl}:","|".join([s[1] for s in cxn.execute(f"PRAGMA TABLE_INFO('{tbl}')")]))
        for row in cxn.execute(f"SELECT * FROM {tbl};"):
            print(row)

if __name__ == "__main__":
    if os.path.exists(_DB_DIR) is False:
        os.mkdir(_DB_DIR)
    cxn = create_db_schema()
    try:
        populate_constant_tables(cxn)
        populate_fuse_product_metadata(cxn,"_work/fuse_data/all_products.xml")
        populate_tone_lt_product_metadata(cxn,None)        
        populate_tone_mobile_product_metadata(cxn,None)        
        dump(cxn)
    except:
        traceback.print_exc()
        dump(cxn)

