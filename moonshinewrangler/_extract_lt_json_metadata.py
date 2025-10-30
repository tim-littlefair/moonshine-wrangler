# python3
# _extract_lt_json_metadata.py
# Author: Tim Littlefair, October 2025-
# The purpose of this script is extract and process
# useful JSON metadata available from running the
# 'strings' utility on the Fender Tone LT Desktop
# executable.

import hashlib
import json
import os
import sys

import _get_working_resources as _GWR


def find_fender_lt_json_snippets(tone_lt_dir, filter_string):
    fender_tone_macos_executable_bytes = _GWR.extract_file_bytes_from_dmg(
        "_work/reference_files/Fender%20Tone.dmg",
        "Fender Tone LT Desktop.app/Contents/MacOS/Fender Tone LT Desktop"
    )
    fender_tone_macos_executable_strings = _GWR.extract_strings_from_file_bytes(
        fender_tone_macos_executable_bytes
    )
    json_dict_objects = {}
    candidate_lineno = 0
    for candidate_text in fender_tone_macos_executable_strings:
        try:
            candidate_lineno += 1
            candidate_dict = json.loads(candidate_text)
            if not isinstance(candidate_dict, dict):
                # The line of text was decodeable as JSON but did not
                # deserialize to a dictionary
                # Expected for integers, floats and strings which match
                # JSON constants like null, true, false
                continue
            if len(candidate_dict.keys()) == 0:
                # There are a few empty dictionaries, clearly these
                # are not interesting
                continue

            # The extracted data contains quite a few records which are not
            # exact duplicates, but contain content which is exactly equivalent
            # under JSON interpretation rules.
            # For example, dictionaries with keys in different orders, floating
            # point numbers with the same value but different numbers of trailing
            # zeroes.
            # We merge these duplicates by reserializing candidate_dict with settings
            # which eliminate these differences.
            # Note that this does not achieve a merger of duplicates which arise out
            # of different orderings of the audioGraph.nodes and audioGraph.connections
            # arrays, although the ordering of both of these arrays is ignored by
            # Fender's software.
            # The ordering of modules in factory presets for Mustang LT- series
            # is always stomp-mod-amp-delay-reverb.
            # The ordering of modules in factory presets for Rumble LT25 series
            # is always stomp-mod-amp-reverb-equalizer.
            # I do not yet know whether these orders are hard-coded in the amp software,
            # but in every case I have seen so far, the order of effects can be determined
            # by looking at the input.nodeId and output.nodeId values of elements under
            # the audioGraph.connections array, starting with the elements with
            # input.nodeId="preset", traversing tracing output.nodeId values to the element
            # where they are used as input.nodeId, and following the sequence through until
            # all elements have been visited and output.nodeId is equal to "preset".
            # TODO: This comment probably needs to be somewhere other than in a Python
            # source file.
            candidate_pretty_json = json.dumps(candidate_dict, indent=4, sort_keys=True)
            candidate_pretty_hash = hashlib.sha256(candidate_pretty_json.encode("utf-8")).hexdigest()[0:7]
            if candidate_pretty_hash not in json_dict_objects.keys():

                # First occurrence of a particular canonical JSON text has been seen

                node_type = candidate_dict.get("nodeType", "module_list")
                if node_type == "dspUnit":
                    node_type = candidate_dict.get("info", {}).get("subcategory", "unknown_dsp_unit_type")

                node_name = "invalid"
                try:
                    if node_type == "module_list":
                        node_name = candidate_dict["productFamily"]
                    elif node_type == "preset":
                        node_name = _GWR.filter_name_chars(candidate_dict["info"]["displayName"])
                    else:
                        # presumably an effect or a utility
                        node_name = candidate_dict["FenderId"]
                except KeyError:
                    print(
                        f"Unable to derive name for node of type {node_type} with keys [{','.join(candidate_dict.keys())}]",
                        file=sys.stderr
                    )
                    continue

                # The LT data captured includes metadata associated with the
                # Fender Rumble LT25 as well as the Mustang LT25/LT40S/LT50
                # amps.
                # We use the filter_string parameter to restrict the data
                # captured to one family or the other so that we have
                # less data to plough through.
                if node_type == "preset" and filter_string not in candidate_text:
                    continue

                candidate_fname = f"{node_type}-{node_name}-{candidate_pretty_hash}.json"
                json_dict_objects[candidate_pretty_hash] = [
                    candidate_fname, candidate_pretty_json, [str(candidate_lineno),]
                ]
            else:
                # Second or later occurrence of a particular pattern has been seen
                json_dict_objects[candidate_pretty_hash][2] += [str(candidate_lineno),]
        except json.decoder.JSONDecodeError:
            # print(candidate_text)
            continue
    # All snippets have been processed - dump the valid ones
    os.makedirs(tone_lt_dir, exist_ok=True)
    for fname, text, lines in sorted(json_dict_objects.values()):
        line_list = ", ".join(lines)
        open(os.path.join(tone_lt_dir, fname), "wt").write(text)
        print(f"{fname} found at line(s): {line_list}")


if __name__ == "__main__":
    find_fender_lt_json_snippets("_work/tone_mustang_lt_data", "mustang")
    # find_fender_lt_json_snippets("_work/tone_rumble_lt_data", "rumble")
