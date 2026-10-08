#! python

# process_tone_mobile_xapk.py

import os
import shutil
import subprocess
import sys

from helpers import extract_streams_and_paths
from helpers import find_strings

_TONE_MOBILE_XAPK_PATH = "./_work/reference_files/Fender+Tone_5.1.3.112680_APKPure.xapk"
_TONE_MOBILE_DATA = "./_work/tone_mobile_data"

def extract_product_json():
    if os.path.exists(_TONE_MOBILE_XAPK_PATH) is False:
        print(f"{_TONE_MOBILE_XAPK_PATH} not found",file=sys.stderr)
        sys.exit(1)

    shutil.rmtree(_TONE_MOBILE_DATA,ignore_errors=True)

    streams_and_paths = extract_streams_and_paths(
        _TONE_MOBILE_XAPK_PATH,
        extension_list = [ ".xapk", ".apk", ".zip" ]
    )
    print("\n".join([str(s_and_p) for s_and_p in streams_and_paths]))
    for s,p,_ in streams_and_paths:
        if p == "config.arm64_v8a.apk":
            find_strings(s, p, _TONE_MOBILE_DATA)

def extract_fenderid_roots():
    dubs_prefix_regex = "DUBS_[[:alnum:]_]+"
    acd_prefix_regex = "ACD_[[:alnum:]_]+"
    grep_cmd = f"grep -h -E -o -e {dubs_prefix_regex} -e {acd_prefix_regex} {_TONE_MOBILE_DATA}/productFamily-*.json|sort|uniq"
    grep_result = subprocess.run(grep_cmd, shell=True, text=True, capture_output=True)
    grep_result.check_returncode()
    all_fender_ids = grep_result.stdout.strip().split("\n")
    all_fid_suffixes = [
        fid.replace("DUBS_","").replace("ACD_","")
        for fid in all_fender_ids
    ]
    all_fid_suffixes.sort()
    last_suffix = "_"
    all_fid_roots = []
    for fid_root in all_fid_suffixes:
        if fid_root == last_suffix:
            continue
        else:
            all_fid_roots += [ fid_root ]
        last_suffix=fid_root
    return all_fid_roots

def group_fids_into_families(all_fid_roots):
    fid_roots_to_process = list(reversed(all_fid_roots))
    fid_families = {}
    while len(fid_roots_to_process)>0:
        next_fid_root = fid_roots_to_process.pop()
        variants = []
        if next_fid_root in ("Fuzz",):
            # There are multiple effects containing the 
            # substring Fuzz which we do not wish to 
            # treat as variants of a common family
            # TBD: Are there any other substrings
            # we need to handle here
            pass
        else:
            for variant_candidate in fid_roots_to_process:
                if next_fid_root in variant_candidate:
                    variants += [ variant_candidate ]
                    fid_roots_to_process.remove(variant_candidate)
                else:
                    pass
        fid_families[next_fid_root] = variants
    return fid_families

if __name__ == "__main__":
    extract_product_json()
    all_fid_roots = extract_fenderid_roots()
    fid_roots_sorted_by_length = sorted(all_fid_roots,key=len)
    fid_families = group_fids_into_families(fid_roots_sorted_by_length)
    print(sorted(fid_families.keys()))
    print(len(fid_families.keys()))


