#! python

# process_tone_mobile_xapk.py

import shutil

from helpers import extract_streams_and_paths
from helpers import find_strings


if __name__ == "__main__":
    _TONE_MOBILE_XAPK_PATH = "./_work/reference_files/Fender Tone_5.0.2.108713_APKPure.xapk"
    _TONE_MOBILE_DATA = "./_work/tone_mobile_data"

    shutil.rmtree(_TONE_MOBILE_DATA,ignore_errors=True)

    streams_and_paths = extract_streams_and_paths(
        _TONE_MOBILE_XAPK_PATH,
        extension_list = [ ".xapk", ".apk", ".zip" ]
    )
    print("\n".join([str(s_and_p) for s_and_p in streams_and_paths]))
    for s,p,_ in streams_and_paths:
        find_strings(s, p, _TONE_MOBILE_DATA)

