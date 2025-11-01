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


def extract_file_bytes_from_dmg(dmg_path, file_entry_path):
    extract_cmd = f"/usr/bin/7z x {dmg_path} -so '{file_entry_path}'"
    sp_result = subprocess.run(extract_cmd, shell=True, capture_output=True)
    assert sp_result.returncode == 0
    return sp_result.stdout


def extract_strings_from_file_bytes(file_bytes):
    extract_cmd = "/usr/bin/strings"
    sp_result = subprocess.run(
        extract_cmd, shell=True, capture_output=True,
        input=file_bytes
    )
    assert sp_result.returncode == 0
    return str(sp_result.stdout, "UTF-8").split("\n")


def filter_name_chars(s):
    s = s.replace(" ", "_")
    return "".join([char for char in s if char.isalnum() or char == "_"])


def filter_fender_id(s):
    regex_list = ("DUBS_Mustang", "DUBS_", "Reverb", "ACD_", "GT")
    for regex in regex_list:
        s = s.replace(regex, "")
    return s


if __name__ == "__main__":
    get_reference_files("_work/reference_files")
