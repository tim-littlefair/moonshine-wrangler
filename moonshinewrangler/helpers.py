import os
import re
import subprocess
import zipfile


_log_level_prefix = ""
_LOG_PER_LEVEL_INDENT = "    "


def extract_streams_and_paths(xapk_path, config_apk_path):
    retval = []
    xapk_zf = zipfile.ZipFile(xapk_path)
    config_apk_zf = zipfile.ZipFile(xapk_zf.open(config_apk_path))
    global _log_level_prefix
    print(f"{_log_level_prefix}Processing streams extracted from {xapk_path}")
    old_log_level_prefix = _log_level_prefix
    _log_level_prefix += _LOG_PER_LEVEL_INDENT
    for zi in config_apk_zf.filelist:
        stream = config_apk_zf.open(zi.filename)
        retval += [ (stream, zi.filename), ]
    _log_level_prefix += old_log_level_prefix
    return retval


def find_strings(stream_from_apk, apk_path, tone_mobile_dir):
    os.makedirs(tone_mobile_dir, exist_ok=True)
    global _log_level_prefix
    print(f"{_log_level_prefix}Processing {apk_path}")
    old_log_level_prefix = _log_level_prefix
    _log_level_prefix += _LOG_PER_LEVEL_INDENT
    strings_result = subprocess.run(
        '/bin/sh -c "/usr/bin/strings -n 10 --include-all-whitespace --output-separator ^"',
        capture_output=True, text=False, shell=True,
        input=stream_from_apk.read(),
    )
    _JSON_PREFIX_PATTERN = re.compile(r'\{\s*"([^"]+)":\s*"([^"]+)"')
    other_strings = []
    for s in strings_result.stdout.split(b'^'):
        candidate_string = str(s,"utf-8")
        match = _JSON_PREFIX_PATTERN.match(candidate_string)
        if match is not None:
            fname = f"{tone_mobile_dir}/{match.group(1)}-{match.group(2)}.json"
            print(f"{_log_level_prefix}{fname} found in {apk_path}")
            open(fname,"wt").write(candidate_string)
        elif "\n" not in candidate_string:
            continue
        else:
            other_strings += [ candidate_string.strip() ]
    if len(other_strings)>0:
        other_strings_fname = f"{tone_mobile_dir}/other_strings-{os.path.basename(apk_path)}.txt"
        other_strings_stream = open(other_strings_fname,"wt")
        other_strings_stream.write("\n^^^^^^^^^^^\n".join(other_strings))
        print(f"{_log_level_prefix}Wrote {len(other_strings)} other strings to {other_strings_fname}")
    _log_level_prefix = old_log_level_prefix


