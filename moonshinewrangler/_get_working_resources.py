# python3
# _get_working_resources.py
# Author: Tim Littlefair, October 2025-
# The purpose of this script is to provide a standardized method of
# acquiring all of the reference files used by the build of this
# library which, for copyright and other reasons, we prefer not
# to store in version control.

import os
import requests
import subprocess

_REFERENCE_FILE_URLS = (
    # The following URLs are for Wayback Machine/archive.org saves of files published by FMIC
    'https://web.archive.org/web/20170403031521/http://www.fmicassets.com/fender/support/software/fender_software/fender_fuse/pc/FenderFUSE_FULL_2.7.1.exe',
    'https://web.archive.org/web/20170403031521/http://www.fmicassets.com/fender/support/software/fender_software/fender_fuse/mac/FenderFUSE_FULL_2.7.1.dmg',
    'https://web.archive.org/web/20241223024259/https://download.fender.com/tone/windows/Fender%20Tone.msi',
    'https://web.archive.org/web/20241223024259/https://download.fender.com/tone/macos/Fender%20Tone.dmg',

    # The following documents published by FMIC were only available on guitarpedaldemos.com at the time this project was initiated
    'https://web.archive.org/web/20250604021422/https://guitarpedaldemos.com/wp-content/uploads/2020/04/MustangI-V_v.2_advanced_manual_revA_English.pdf',
    'https://web.archive.org/web/20250815193142/https://guitarpedaldemos.com/wp-content/uploads/2025/06/Fender_FUSE_2.0_manual_for__Mustang_1-2_Rev-G_English.pdf',

    # The following files are sourced from:
    # https://guitarpedaldemos.com/fender-fuse-mustang-v2-archive
    # For some reason Wayback Machine/archive.org fails to capture them
    'https://guitarpedaldemos.com/wp-content/uploads/2020/04/entire-archive.zip',
    'https://guitarpedaldemos.com/wp-content/uploads/2020/04/intheblues.zip',
    'https://guitarpedaldemos.com/wp-content/uploads/2020/04/factory-presets.zip',
)


def get_reference_files(target_dir):
    os.makedirs(target_dir, exist_ok=True)
    for url in _REFERENCE_FILE_URLS:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        save_path = os.path.join(target_dir, os.path.basename(url))
        if os.path.exists(save_path):
            print(f"{save_path} already found (not checked)")
            continue
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=102400):
                f.write(chunk)
        print(f"{save_path} saved")


def _extract_file_bytes_from_dmg(dmg_path, file_entry_path):
    extract_cmd = f"/usr/bin/7z x {dmg_path} -so '{file_entry_path}'"
    sp_result = subprocess.run(extract_cmd, shell=True, capture_output=True)
    assert sp_result.returncode == 0
    return sp_result.stdout


def _extract_strings_from_file_bytes(file_bytes):
    extract_cmd = "/usr/bin/strings"
    sp_result = subprocess.run(
        extract_cmd, shell=True, capture_output=True,
        input=file_bytes
    )
    assert sp_result.returncode == 0
    return str(sp_result.stdout, "UTF-8").split("\n")


def find_fender_lt_json_snippets():
    fender_tone_macos_executable_bytes = _extract_file_bytes_from_dmg(
        "_work/reference_files/Fender%20Tone.dmg",
        "Fender Tone LT Desktop.app/Contents/MacOS/Fender Tone LT Desktop"
    )
    fender_tone_macos_executable_strings = _extract_strings_from_file_bytes(
        fender_tone_macos_executable_bytes
    )
    fender_lt_json_snippets = [
        line
        for line in fender_tone_macos_executable_strings
        if "nodeType" in line
    ]
    return fender_lt_json_snippets


def extract_fender_fuse_exe_strings():
    pax_archive_bytes = _extract_file_bytes_from_dmg(
        "_work/reference_files/FenderFUSE_FULL_2.7.1.dmg",
        "Fender FUSE Installer/Fender FUSE Installer.app/Contents/Resources/Fender FUSE.pkg/Contents/Archive.pax.gz"
    )
    # fuse_exe_path_within_pax = "./Applications/Fender FUSE.app/Contents/Resources/FenderFUSE.app/Contents/Resources/FenderFUSE.exe"
    # The output of pax_cmd is actually a pax archive,
    # but the only file it contains is the FUSE
    # (Windows/Mono/Silverlight) executable so
    # we run strings on it as if it were the bare executable
    # pax_cmd = f"/usr/bin/gzip -d | /usr/bin/pax -r -w {fuse_exe_path_within_pax} | /usr/bin/strings"
    # pax_cmd = f"/usr/bin/gzip -d | /usr/bin/pax -r '{fuse_exe_path_within_pax}' -w -x tar -o write_opt=nodir | /usr/bin/strings"
    pax_cmd = "/usr/bin/gzip -d | /usr/bin/strings"
    sp_result = subprocess.run(
        pax_cmd, shell=True, capture_output=True,
        input=pax_archive_bytes
    )
    assert sp_result.returncode == 0
    return str(sp_result.stdout, "UTF-8").split("\n")


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
    get_reference_files("_work/reference_files")
    find_fender_lt_json_snippets()
    extract_fender_fuse_db_xml("_work/fuse_data/mustang_I_II_V2_range.xml")
