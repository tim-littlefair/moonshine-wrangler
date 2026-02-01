#! python

# process_tone_mobile_xapk.py

import os
import re
import subprocess
import zipfile


def extract_mustang_so(xapk_path, config_apk_path, mustang_so_path):
    xapk_zf = zipfile.ZipFile(xapk_path)
    config_apk_zf = zipfile.ZipFile(xapk_zf.open(config_apk_path))
    mustang_so_stream = config_apk_zf.open(mustang_so_path)
    return mustang_so_stream

def find_json_strings(mustang_so_stream, tone_mobile_dir):
    os.makedirs(tone_mobile_dir, exist_ok=True)    
    strings_result = subprocess.run(
        '/bin/sh -c "/usr/bin/strings -n 10 --include-all-whitespace --output-separator ^"',
        capture_output=True, text=False, shell=True,
        input=mustang_so_stream.read(),
    )
    _JSON_PREFIX_PATTERN = re.compile(r'\{\s*"([^"]+)":\s*"([^"]+)"')
    other_strings = []
    for s in strings_result.stdout.split(b'^'):
        candidate_string = str(s,"utf-8")
        match = _JSON_PREFIX_PATTERN.match(candidate_string)
        if match is not None:
            fname = f"{tone_mobile_dir}/{match.group(1)}-{match.group(2)}.json"
            print(f"Dumping to {fname}")
            open(fname,"wt").write(candidate_string)
        elif "\n" not in candidate_string:
            continue
        else:
            other_strings += [ candidate_string ]
        other_strings_stream = open(f"{tone_mobile_dir}/other_strings.txt","wt")
        other_strings_stream.write("\n^^^^^^^^^^^\n".join(other_strings))

if __name__ == "__main__":
    _TONE_MOBILE_XAPK_PATH = "./_work/reference_files/Fender Tone_5.0.2.108713_APKPure.xapk"
    _CONFIG_APK_PATH = "config.arm64_v8a.apk"
    _MUSTANG_SO_PATH = "lib/arm64-v8a/libmustangdevice.so"

    mustang_so_stream = extract_mustang_so(
        _TONE_MOBILE_XAPK_PATH,
        _CONFIG_APK_PATH,
        _MUSTANG_SO_PATH
    )
    find_json_strings(mustang_so_stream, "./_work/tone_mobile_dir")




