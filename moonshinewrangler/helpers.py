import os
import re
import subprocess
import zipfile


_log_level_prefix = ""
_LOG_PER_LEVEL_INDENT = "    "

# extract_streams_and_paths accepts a parameter which can be a simple string
# for archives directly in the filesystem, or tuple of order 3 for 
# nested archives (which may be nested to any depth).
# The nested archive tuple consists of:
# + the name of the item to be extracted relative to the innermost archive
# + the extracted byte stream for the item
# + a list of paths to nesting archives, beginning with filesystem path to 
#   the outermost archive, ending with the innermost archive (outermost
#   and innermost may be the same item)

def _fn(archive_path):
    if isinstance(archive_path,str):
        return archive_path
    else:
        _check_archive_tuple(archive_path)
        return archive_path[0]

def _check_archive_tuple(archive_path):
    assert isinstance(archive_path, tuple)
    assert len(archive_path)==3

def _stream(archive_path):
    _check_archive_tuple(archive_path)
    return archive_path[1]

def _nesting_archives(archive_path):
    _check_archive_tuple(archive_path)
    return ":".join(archive_path[2])


def extract_streams_and_paths(archive_path, extension_list = [ ".xapk", ".apk", ".zip"]):
    global _log_level_prefix
    print(f"{_log_level_prefix}Processing streams extracted from {_fn(archive_path)}")
    archive_zf = None
    if isinstance(archive_path,str):
        archive_zf = zipfile.ZipFile(archive_path)
    else: 
        archive_zf = zipfile.ZipFile(_stream(archive_path))
    retval = []
    for zi in archive_zf.filelist:
        #print(zi.filename)
        for ext in extension_list:
            if zi.filename.endswith(ext):
                #print(zi.filename+ " is an archive with extension " + ext)
                old_log_level_prefix = _log_level_prefix
                _log_level_prefix += _LOG_PER_LEVEL_INDENT
                next_level_archive_path = (zi.filename, archive_zf.open(zi.filename), None)
                retval += extract_streams_and_paths(next_level_archive_path,extension_list)
                _log_level_prefix = old_log_level_prefix
                continue
        # If none of the archive extensions matched, process as a simple stream
        #print(zi.filename+ " is not an archive")
        stream = archive_zf.open(zi.filename)
        retval += [ (stream, zi.filename, None), ]
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


