# python3
# _get_working_resources.py
# Author: Tim Littlefair, October 2025-
# The purpose of this script is to provide a standardized method of
# acquiring all of the reference files used by the build of this
# library which, for copyright and other reasons, we prefer not
# to store in version control.

import os
import subprocess


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
    # product or group of products supported by the application.
    # We choose to preserve only one <Product> element, the one
    # associated with name "Mustang V2 I/II".
    line_array_index = 0
    preserve_lines = False
    while line_array_index < len(fuse_exe_strings):
        line = fuse_exe_strings[line_array_index]
        if "</FXDataBase>" in line:
            fuse_fx_db_lines += [line, '']
            break
        elif preserve_lines is True:
            fuse_fx_db_lines += [line]
            if '</Product>' in line:
                preserve_lines = False
        if line.startswith("<FXDataBase "):
            previous_line = fuse_exe_strings[line_array_index-1]
            assert '<?xml version="1.0" encoding="utf-8"?>' in previous_line
            fuse_fx_db_lines += [previous_line, line]
        elif '<Product Name="Mustang V2 I/II" ID="13">' in line:
            fuse_fx_db_lines += [line]
            preserve_lines = True
        line_array_index += 1
    fuse_db_xml = "\n".join(fuse_fx_db_lines)
    os.makedirs(os.path.dirname(fuse_xml_path), exist_ok=True)
    open(fuse_xml_path, "wt").write(fuse_db_xml)
    print(f"Fender FUSE database for Mustang V2 I/II extracted to {fuse_xml_path}")


if __name__ == "__main__":
    extract_fender_fuse_db_xml("_work/fuse_data/mustang_I_II_V2_range.xml")
