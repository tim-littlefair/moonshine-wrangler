#! python

# process_tone_mobile_xapk.py

import os
import re
import subprocess
import zipfile

from helpers import extract_streams_and_paths
from helpers import find_strings


if __name__ == "__main__":
    _TONE_MOBILE_XAPK_PATH = "./_work/reference_files/Fender Tone_5.0.2.108713_APKPure.xapk"
    _CONFIG_APK_PATH = "config.arm64_v8a.apk"

    streams_and_paths = extract_streams_and_paths(
        _TONE_MOBILE_XAPK_PATH,
        _CONFIG_APK_PATH
    )
    for s,p in streams_and_paths:
        find_strings(s, p, "./_work/tone_mobile_dir")




