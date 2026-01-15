# python3
# _extract_lt_json_metadata.py
# Author: Tim Littlefair, October 2025-
# The purpose of this script is extract and process
# useful JSON metadata available from running the
# 'strings' utility on the Fender Tone LT Desktop
# executable.

# IMPLEMENTATION NOTE
# The extracted data contains quite a few records which are not
# exact duplicates, but contain content which is exactly equivalent
# under JSON interpretation rules.
# For example, dictionaries with keys in different orders, floating
# point numbers with the same value but different numbers of trailing
# zeroes are considered equivalent when parsing JSON.
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

import copy
import hashlib
import json
import os
import sys

import _get_working_resources as _GWR


def _make_preset_canonical(candidate_dict):
    # This function assumes and asserts that the audio chain is either
    # stomp-mod-amp-reverb-delay (for Mustang LT- 25, 40S, 50 and MMP) or
    # stomp-mod-amp-eq-delay (for Rumble LT-25 only).
    # The older Mustang I-V V2 series or higher-end GT-, GTX- series may
    # be capable of operating effects in orders varying for this - I don't
    # know whether these can be replicated on the models covered by this
    # software.

    if len(candidate_dict["audioGraph"]["nodes"]) != 5:
        return None

    # We retain a deep copy of the original dict in case assertions here
    # fail and we want to restore the initial state before exiting.
    original_dict = copy.deepcopy(candidate_dict)

    # The audioGraph.connections array models a set of cables connecting
    # input, through effect and amp modules, through to output, but is
    # very verbose, and redundant if we make the assumption described
    # in the comment above, so we remove it.
    del candidate_dict["audioGraph"]["connections"]

    # The audioGraph.nodes array gives all of the effects and parameters
    # but the order of items in the array is random and does not reflect
    # the module processing order.  By sorting it into the expected order
    # described in the top of function comment we ensure that the canonical
    # preset retains an explicit expression of the assumed order.

    # Some presets have multiple variants which differ only in
    # whether nodes with FenderId DUBS_Passthru have explicit
    # bypass and bypassMode parameters.  This setting is irrelevant for
    # passthru nodes, so we remove this source of difference.

    # Finally, we filter the FenderId of the node to remove prefixes
    # and suffixes which differ between LT- and MMP- ranges.
    required_order = None
    if candidate_dict["info"]["product_id"] == "rumble-lt":
        required_order = ("stomp", "mod", "amp", "eq", "delay")
    else:
        required_order = ("stomp", "mod", "amp", "delay", "reverb")
    original_nodes = candidate_dict["audioGraph"]["nodes"]
    reordered_nodes = [None, None, None, None, None]
    for i in range(0, 5):
        try:
            (next_node,) = [
                a_node
                for a_node in original_nodes
                if (
                    a_node["nodeId"] == required_order[i]
                    # or a_node["nodeId"].replace("eq", "delay") in required_order[i]
                    # or required_order[i].startswith(a_node["nodeId"])
                    # or required_order[i].endswith(a_node["nodeId"])
                )
            ]
            if next_node["FenderId"] == "DUBS_Passthru":
                next_node["dspUnitParameters"] = {}
            next_node["FenderId"] = _GWR.filter_fender_id(next_node["FenderId"])
            reordered_nodes[i] = next_node
        except ValueError:
            print(f"Missing expected node {i} : {required_order[i]}")
            print(f"{[n.get('nodeId', "?").encode("utf-8") for n in original_nodes]}")
            candidate_dict = original_dict
            return None
    candidate_dict["audioGraph"]["nodes"] = reordered_nodes
    return candidate_dict


def _get_node_type_and_name(candidate_dict):
    try:
        node_type = candidate_dict.get("nodeType", "module_list")
        if node_type == "dspUnit":
            # we expect an amp, effect or a utility
            # any of these will have an "info" subobject with keys
            # subcategory and displayName
            info = candidate_dict.get(
                "info", {
                    "subcategory": "unknown_dsp_unit_type",
                    "displayName": "unknown_dsp_unit_name"
                }
            )
            node_type = info["subcategory"]
            node_name = _GWR.filter_fender_id(candidate_dict["FenderId"])
            param_count = len(candidate_dict["ui"]["uiParameters"])
            if param_count > 0:
                node_name += f".{param_count:02}params"
            return node_type, node_name
        elif node_type == "preset":
            node_name = _GWR.filter_name_chars(candidate_dict["info"]["displayName"])
            candidate_dict = _make_preset_canonical(candidate_dict)
            if candidate_dict is not None:
                return node_type, node_name
            elif node_name == "EMPTY_________":
                # ignore these
                pass
            else:
                print(
                    f"Preset with node_name {node_name} cannot be made canonical",
                    file=sys.stderr
                )
            return None
        if node_type == "module_list":
            node_name = candidate_dict["productFamily"]
        else:
            pass
    except KeyError:
        print(
            f"Unable to derive name for node of type {node_type} with keys [{','.join(candidate_dict.keys())}]",
            file=sys.stderr
        )
        return None
    # If we get to here, we expect to have a usable node type and node name
    return node_type, node_name


def find_fender_lt_json_snippets(tone_lt_dir, product_family_name):
    fender_tone_macos_executable_bytes = _GWR.extract_file_bytes_from_dmg(
        "_work/reference_files/Fender%20Tone.dmg",
        "Fender Tone LT Desktop.app/Contents/MacOS/Fender Tone LT Desktop"
    )
    fender_tone_macos_executable_strings = _GWR.extract_strings_from_file_bytes(
        fender_tone_macos_executable_bytes
    )

    json_dict_objects = {}
    candidate_lineno = 0
    product_module_json_text = None
    while candidate_lineno < len(fender_tone_macos_executable_strings):
        try:
            # Note that we choose for candidate_lineno to match the 1-based index
            # of the line in the output if we ran /usr/bin/strings by hand,
            # not the 0-based array subscript.
            candidate_text = fender_tone_macos_executable_strings[candidate_lineno]
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
            node_type_and_name = _get_node_type_and_name(candidate_dict)
            if node_type_and_name is None:
                continue
            node_type, node_name = node_type_and_name
            # print(f"{node_type}:{node_name}@{candidate_lineno}")

            if node_name == product_family_name:
                assert node_type == "module_list"
                if product_module_json_text is None:
                    # This line contains a lists of the amp and effect modules
                    # available on the selected family
                    product_module_json_text = candidate_text
                    # Reset the line number to zero to trigger
                    # reprocessing of all lines already checked
                    candidate_lineno = 0
                    # No further processing on this pass - the line
                    # will be saved to a file with the right line number
                    # when it is reached in the next pass
                    continue
                else:
                    pass
            elif product_module_json_text is None:
                # We haven't seen the module_list node yet so
                # we don't know which effects to preserve and
                # which to ignore.
                # Ignore for now, this line will be processed again after
                # the module list is seen and the line number is reset.
                continue

            candidate_pretty_json = json.dumps(candidate_dict, indent=4, sort_keys=True)
            candidate_pretty_hash = hashlib.sha256(candidate_pretty_json.encode("utf-8")).hexdigest()[0:7]
            if candidate_pretty_hash not in json_dict_objects.keys():

                # First occurrence of a particular canonical JSON text has been seen

                # The LT data captured includes metadata associated with the
                # Fender Rumble LT25 as well as the Mustang LT25/LT40S/LT50
                # amps.
                # We use the product_family_name parameter to restrict the data
                # captured to one family or the other so that we have
                # less data to plough through.
                if node_type == "preset" and product_family_name in candidate_text:
                    pass
                elif node_type == "preset":
                    continue
                elif product_module_json_text is not None:
                    candidate_fenderid = candidate_dict.get("FenderId", "")
                    if candidate_fenderid not in product_module_json_text:
                        # print(f"Filtering candidate of type {node_type} with FenderId {candidate_fenderid}")
                        continue
                    else:
                        pass

                candidate_fname = f"{node_type}-{node_name}-{candidate_pretty_hash}.json"
                json_dict_objects[candidate_pretty_hash] = [
                    candidate_fname, candidate_pretty_json, [str(candidate_lineno),]
                ]
            else:
                # Second or later occurrence of a particular pattern has been seen
                json_dict_objects[candidate_pretty_hash][2] += [str(candidate_lineno),]
        except json.decoder.JSONDecodeError:
            continue
    # All snippets have been processed - dump the valid ones
    os.makedirs(tone_lt_dir, exist_ok=True)
    for fname, text, lines in sorted(json_dict_objects.values()):
        line_list = ", ".join(lines)
        open(os.path.join(tone_lt_dir, fname), "wt").write(text)
        print(f"{fname} found at line(s): {line_list}")


if __name__ == "__main__":
    find_fender_lt_json_snippets("_work/tone_mustang_lt_data", "mustang")
    find_fender_lt_json_snippets("_work/tone_rumble_lt_data", "rumble")
