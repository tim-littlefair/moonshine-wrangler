# python3
# _get_working_resources.py
# Author: Tim Littlefair, October 2025-
# The purpose of this script is to provide a standardized method of
# acquiring all of the reference files used by the build of this
# library which, for copyright and other reasons, we prefer not
# to store in version control.

import hashlib
import os
import requests
import subprocess


_REFERENCE_FILE_URLS = (

    ## Fender Tone mobile application
    # This application runs on iPadOS/iOS/Android, and interoperates with the 
    # following FMIC device series: Mustang GT/GTX/LTX, Mustang Micro Plus
    
    # There does not appear to be any way of obtaining the Fender Tone .ipa installer for iPad/iPhone,
    # but the the .apk installer for Android is available from:
    # https://fender-tone.en.uptodown.com/android via a sequence of manual clicks leading to a lengthy 
    # generated URL which presumably only remains downloadable for a short time so can't be used
    # in a script.
    # As at 14 December 2025, the latest version has filename 'fender-tone-3-3-1.apk' and 
    # SHA256 3f1a982281d685263b370ffb168a1641d502120298055a63c7f05e7dd7ef0600
    # As at the same date, the  apkpure.com URL below retrieves file with the name 
    # 'Fender Tone_3.3.1_APKPure.apk' and the same SHA256.
    # According to Google Chrome searches on 'uptodown.com reputation' and 'apkpure reputationn'
    # as at the same date, the uptodown site is regarded as trustworthy, while apkpure has 
    # a mixed repututation.  This package will use the apkpure.com link to download the file
    # but will verify that it has the same SHA256 hash as the manually downloaded file from 
    # the more trusted site before allowing it to be used in any way.
    'https://d.apkpure.com/b/APK/com.fender.tone?versionCode=13989&nc=&sv=23',
    
    ## Fender Tone LT Desktop application
    # This application runs on macOS/Windows and operates with the Mustang LT and Rumble LT 
    # FMIC device series.
    'https://web.archive.org/web/20241223024259/https://download.fender.com/tone/windows/Fender%20Tone.msi',
    'https://web.archive.org/web/20241223024259/https://download.fender.com/tone/macos/Fender%20Tone.dmg',
    
    
    ## Fender FUSE application
    # This application runs on macOS and Windows (withdrawn from distribution by FMIC around 2019,
    # may not run on some variants of either OS later than that).
    # This application interoperates with the FMIC devices in the v1 and v2 variants of the 
    # Mustang I, II, III, IV, V sequence of  models
    # The following URLs are for Wayback Machine/archive.org saves of installer files originally published 
    # on FMIC's website
    'https://web.archive.org/web/20170403031521/http://www.fmicassets.com/fender/support/software/fender_software/fender_fuse/pc/FenderFUSE_FULL_2.7.1.exe',
    'https://web.archive.org/web/20170403031521/http://www.fmicassets.com/fender/support/software/fender_software/fender_fuse/mac/FenderFUSE_FULL_2.7.1.dmg',

    # Manuals for the Fender FUSE software
    # The following documents published by FMIC were only available on guitarpedaldemos.com at the time this project was initiated
    'https://web.archive.org/web/20250604021422/https://guitarpedaldemos.com/wp-content/uploads/2020/04/MustangI-V_v.2_advanced_manual_revA_English.pdf',
    'https://web.archive.org/web/20250815193142/https://guitarpedaldemos.com/wp-content/uploads/2025/06/Fender_FUSE_2.0_manual_for__Mustang_1-2_Rev-G_English.pdf',

    ## Portfolio of preset definitions in XML-based .fuse file format 
    # These files were 
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
        request_headers = {}
        save_path = os.path.join(target_dir, os.path.basename(url))
        if 'apkpure' in url:
            save_path=os.path.join(target_dir, 'Fender Tone_3.3.1_APKPure.apk')
            request_headers["Referer"] = "https://apkpure.com/cn/fender-tone/com.fender.tone/download/3.3.1"
        if os.path.exists(save_path):
            print(f"{save_path} already found (not checked)")
            continue
        response = requests.get(url, stream=True,headers=request_headers)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=102400):
                f.write(chunk)
        print(f"{save_path} saved")
        if 'APKPure' in save_path:
            # Verify the SHA256 of the one file retrieved from the suspect site apkpure.com
            h = hashlib.sha256()
            with open(save_path, 'rb') as file:
                while chunk := file.read(8192): 
                    h.update(chunk)
            if h.hexdigest()=='3f1a982281d685263b370ffb168a1641d502120298055a63c7f05e7dd7ef0600':
                print(f"{save_path} matches expected SHA256, will be retained")
            else:
                print(f"{save_path} does not match expected SHA256, will be renamed")
                os.rename(save_path,save_path+".suspicious")


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
