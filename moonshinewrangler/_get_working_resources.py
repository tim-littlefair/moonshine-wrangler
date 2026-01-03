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

_REFERENCE_FILE_EXPECTED_CHECKSUMS = {
    "Fender Tone_5.0.2.108713_APKPure.xapk": "6dfac9cbd119ba54e8f53236fcaa1b9e994ad75006c96220c01e0261f1746430",
    "Fender%20Tone.dmg": "be78cbb8528af3c702d0e9b41d6002ea3ff5f1ffab253b2f4f5407ab881041fb",
    "Fender%20Tone.msi": "52884540ceae1f7dc507e5a387dbb31c6083c1747f6e2a83c53b8e1dff69fb29",
    "FenderFUSE_FULL_2.7.1.dmg": "e68de1a1c1068d34dda354e2678ddac4a796b2ccdface95b034a438455442919",
    "FenderFUSE_FULL_2.7.1.exe": "38bb32a2dff5549067efb99aa1d4caf70331a1b67b2882cf97fcea97c4d09f26",
    "Fender_FUSE_2.0_manual_for__Mustang_1-2_Rev-G_English.pdf": "a74017efbdcf5eb746ec9946281b3075d496153b016fcecbc678fd43dce6ee8c",
    "Mustang1_1.9.upd": "ba216b118dbee89b7f6949dcd03e699a7042471aaba746c6264e967c0844ac87",
    "Mustang3_1.9.upd": "33e52d26dff5ced81a3f3f97edf0d674ebaf9de4d859ed4b4e93702d92d032c4",
    "MustangFloor_1.3.upd": "3520955c7c2e18595ac3d132e5e645b3edb84ae47b2ff7f56f6956f8f54290e1",
    "MustangFloor_1.4.zip": "d4073df1dfae01d8ac36de5a1590e4d5931f65b2aa73a9163f50c2211022c21f",
    "MustangI-II_1.10.zip": "d338c4de73d3c9ce05ff57cb08a0ec8966b39ce36d350a5a365fa56b70c8b4ec",
    "MustangI-V_v.2_advanced_manual_revA_English.pdf": "211ff31cfaa16be6c6720c5c2844455355d9846835c1b01956f9759d285e740f",
    "MustangIII-V_1.10.zip": "d0b9b865d91f3bfe38744309e894fe3ff5ef1e8d5cd75a09b8afcb2bd1fd741d",
    "V2_Mustang1_2.2.zip": "b8542354fd396cc37da615a2abf07c85c706186f8d9325b588ba03de7918d962",
    "V2_Mustang3_2.2.zip": "80a23011bfafa738cef78e8a10ac15df58320217d0e0af323cf5566093079492",
    "entire-archive.zip": "562301403fa77b4e9ea09eb21f0a043be0aff7a2278a517151c7aef1c3ebd785",
    "factory-presets.zip": "6579c4ab6ecc3af6245d43b6ec075ff81da649e8c57b5fd6d5514fa9a430b6a0",
    "intheblues.zip": "87def677aedaee5e4dc5dfcd6a7767916696802c56fb1eba8778f634429b30f9"
}

# URLS which, as at 3/1/2026, can be used programmatically to download reference files listed above
_REFERENCE_FILE_DIRECT_URLS = (
    ## The following URLs are for Wayback Machine/archive.org saves of installers published by FMIC for 
    ## the following companion apps:
    # + Fender FUSE (interoperating with classic v1/v2 Mustangs)
    'https://web.archive.org/web/20170403031521/http://www.fmicassets.com/fender/support/software/fender_software/fender_fuse/pc/FenderFUSE_FULL_2.7.1.exe',
    'https://web.archive.org/web/20170403031521/http://www.fmicassets.com/fender/support/software/fender_software/fender_fuse/mac/FenderFUSE_FULL_2.7.1.dmg',
    # + Fender Tone LT Desktop (interoperating with LT- series Mustangs - but not LTX- series)
    'https://web.archive.org/web/20241223024259/https://download.fender.com/tone/windows/Fender%20Tone.msi',
    'https://web.archive.org/web/20241223024259/https://download.fender.com/tone/macos/Fender%20Tone.dmg',

    # The following documents published by FMIC were only available on archive.org at the time this project was initiated
    'https://web.archive.org/web/20250604021422/https://guitarpedaldemos.com/wp-content/uploads/2020/04/MustangI-V_v.2_advanced_manual_revA_English.pdf',
    'https://web.archive.org/web/20250815193142/https://guitarpedaldemos.com/wp-content/uploads/2025/06/Fender_FUSE_2.0_manual_for__Mustang_1-2_Rev-G_English.pdf',

    # Archives of .fuse files collected and preserved by the user community 
    # directly after Fender took down the web fuse.fender.com infrastructure
    # supporting of sharing of presets in the .fuse format supported by the 
    # Fender FUSE companion app
    # The following files are sourced from:
    # https://guitarpedaldemos.com/fender-fuse-mustang-v2-archive
    # For some reason Wayback Machine/archive.org fails to capture them
    'https://guitarpedaldemos.com/wp-content/uploads/2020/04/entire-archive.zip',
    'https://guitarpedaldemos.com/wp-content/uploads/2020/04/intheblues.zip',
    'https://guitarpedaldemos.com/wp-content/uploads/2020/04/factory-presets.zip',
)

# URLS which, as at 3/1/2026, can be used manually with a browser to download
# files for which no direct URL is known into the reference files directory.
# Expect to need to click through one or two additional links to get the
# target file(s)

_REFERENCE_FILE_MANUAL_URLS = {
    # As at 3/1/2023, page accessible via the following URL 
    # provides click through download links for the following Mustang firmware files:
    "https://drivers.softpedia.com/dyn-search.php?search_term=Fender+Mustang" : (
        "Mustang1_1.9.upd",      # for both (v1) Mustang I and  II
        "Mustang3_1.9.upd",      # for all of (v1) Mustang III, IV and V
        "MustangI-II_1.10.zip",  # also for both (v1) Mustang I and  II
        "MustangIII-V_1.10.zip", # also for all of (v1) Mustang III, IV and V
        "V2_Mustang1_2.2.zip",   # for both of v2 Mustang I amd II
        "V2_Mustang3_2.2.zip",   # for all of v2 Mustang III, IV and V
        "MustangFloor_1.3.upd",  
        "MustangFloor_1.4.zip",  
    ),

    # As at 3/1/2023, page accessible via the following URL 
    # provides a click through download links for the FenderTone
    # Android app for Mustang GT-, GTX-, LTX- series and the 
    # Mustang Micro Plus
    "https://apkpure.com/fender-tone/com.fender.tone" : (
        "Fender Tone_5.0.2.108713_APKPure.xapk",
    ),
}

def checksum(dirname, filename):
    return hashlib.sha256(
        open(os.path.join(dirname,filename),"rb").read()
    ).hexdigest()

def get_reference_files(target_dir):
    os.makedirs(target_dir, exist_ok=True)
    required_files = sorted(_REFERENCE_FILE_EXPECTED_CHECKSUMS.keys())
    files_to_download = []
    files_present_and_correct = []
    files_present_but_incorrect = []
    for f in required_files:
        expected_checksum = _REFERENCE_FILE_EXPECTED_CHECKSUMS[f]
        if not os.path.exists(os.path.join(target_dir, f)):
            files_to_download += [ f ]
        elif checksum(target_dir,f) == expected_checksum:
            files_present_and_correct += [ f ]
        else:
            files_present_but_incorrect += [ f ]
    if len(files_present_and_correct)>0:
        print("\n + ".join(
            [ "The following file(s) are already present and have expected checksum(s):" ] +
            files_present_and_correct
        ))
    if len(files_present_but_incorrect)>0:
        print("\n + ".join(
            [ "The following files are already present but have unexpected checksums:" ] +
            files_present_but_incorrect
        ))
        print("Remove or rename the existing files to re-attempt download")
    files_to_download_manually = {}
    urls_to_download = []
    direct_url_filenames = [ os.path.basename(url) for url in _REFERENCE_FILE_DIRECT_URLS ]
    for f in files_to_download:
        if f in direct_url_filenames:
            urls_to_download += [ 
                url for url in _REFERENCE_FILE_DIRECT_URLS 
                if os.path.basename(url)==f
            ]
        else:
            ( manual_url, ) = [ 
                url for url in _REFERENCE_FILE_MANUAL_URLS.keys()
                if f in _REFERENCE_FILE_MANUAL_URLS[url]
            ]
            files_to_download_manually[manual_url] = (
                files_to_download_manually.get(manual_url,[]) + [f]
            )
    if(len(files_to_download_manually)>0):
        print("The following files are already not present but can be downloaded manually from the URLs shown:")
        for url in files_to_download_manually.keys():
            print("\n  - ".join(
                [ " + " + url ] +
                list(files_to_download_manually[url])
            ))            
    if(len(urls_to_download)>0):
        print("\n + ".join(
            ["Additional files will be downloaded directly from the URLs shown:"] + 
            urls_to_download
        ))
    for url in urls_to_download:
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

    import hashlib
    import json
    import sys

    _REFERENCE_FILE_PATH = "_work/reference_files"  
    get_reference_files(_REFERENCE_FILE_PATH)
    expected_checksums = { }
    actual_checksums = { }
    if False: # enable temporarily when adding new files
        for f in os.listdir(_REFERENCE_FILE_PATH):
            actual_checksums[f]=checksum(_REFERENCE_FILE_PATH,f)
        json.dump(actual_checksums, sys.stdout, indent=4, sort_keys=True)
    