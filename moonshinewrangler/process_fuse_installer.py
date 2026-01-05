# python3
# _get_working_resources.py
# Author: Tim Littlefair, October 2025-
# The purpose of this script is to provide a standardized method of
# acquiring all of the reference files used by the build of this
# library which, for copyright and other reasons, we prefer not
# to store in version control.

import os
import re
import subprocess
import urllib.parse


def _extract_file_bytes_from_dmg(dmg_path, file_entry_path):
    extract_cmd = f"/usr/bin/7z x {dmg_path} -so '{file_entry_path}'"
    sp_result = subprocess.run(extract_cmd, shell=True, capture_output=True)
    assert sp_result.returncode == 0
    return sp_result.stdout


def extract_fender_fuse_exe_strings():
    pax_archive_bytes = _extract_file_bytes_from_dmg(
        "_work/reference_files/FenderFUSE_FULL_2.7.1.dmg",
        "Fender FUSE Installer/Fender FUSE Installer.app/Contents/Resources/Fender FUSE.pkg/Contents/Archive.pax.gz"
    )
    # The byte stream pax_archive_bytes is actually a gzipped pax archive,
    # but the only file it contains is the FUSE (Windows/Mono/Silverlight)
    # binary executable so we run strings on the decompressed stream as
    # if it were the bare executable
    pax_cmd = "/usr/bin/gzip -d | /usr/bin/strings"
    sp_result = subprocess.run(
        pax_cmd, shell=True, capture_output=True,
        input=pax_archive_bytes
    )
    assert sp_result.returncode == 0
    return str(sp_result.stdout, "utf-8").split("\n")


def extract_fender_fuse_db_xml(fuse_xml_path):
    fuse_exe_strings = extract_fender_fuse_exe_strings()
    fuse_fx_db_lines = []
    # The executable inside the archive contains an XML stream with
    # root element with tag <FXDataBase>.
    # Inside the root element there are multiple elements with tag <Product>,
    # each of which contains the parameters applicable for a single
    # (amplifier) product or group of products supported by the FUSE application.
    # We choose to preserve one XML file containing the full data and also 
    # separate XML files for each product/group.
    line_array_index = 0
    full_xml_file = None
    product_xml_file = None
    product_start_regex = re.compile(r'<Product Name="([^"]+)" ID="(\d+)">')
    os.makedirs(fuse_xml_path, exist_ok=True)

    while line_array_index < len(fuse_exe_strings):
        line = fuse_exe_strings[line_array_index]
        if line.startswith("<FXDataBase "):
            assert line_array_index>0
            previous_line = fuse_exe_strings[line_array_index-1]
            assert '<?xml version="1.0" encoding="utf-8"?>' in previous_line
            full_xml_file = open(os.path.join(fuse_xml_path,"all_products.xml"),"wt")
            print(previous_line, file=full_xml_file)
            # current line will be output at end of loop
        elif "</FXDataBase>" in line:
            print(line, file=full_xml_file)
            full_xml_file = None
            break
        elif '</Product>' in line:
            print(line,file=product_xml_file)
            product_xml_file=None
        elif product_start_regex.search(line):
            match = product_start_regex.search(line)
            product_name = match.group(1)
            # make product_name filename safe
            product_name = product_name.replace(" ","_").replace("/","+")
            product_xml_filename = f"product{match.group(2)}-{product_name}.xml"
            product_xml_file = open(os.path.join(fuse_xml_path,product_xml_filename),"wt")
            # current line will be output at end of loop
        for stream in ( full_xml_file, product_xml_file):
            if stream is not None:
                print(line,file=stream)
        line_array_index += 1

if __name__ == "__main__":
    extract_fender_fuse_db_xml("_work/fuse_data")
