# lt_json_to_mobile_params.py

# Script to convert JSON presets extracted from the FenderTone LT Desktop installer
# into approximate UI parameters for use in FenderTone mobile with the MMP.

import io
import json
import os
import sys
import traceback


_DATA_DIR = "_work/tone_lt_data"
_DSP_UNIT_TYPES = ( "stomp", "mod", "amp", "delay", "reverb", )
_PARAMS_TO_IGNORE = (
    "bypass", "bypassType",
    "noteDivision", "tapTimeBPM",
    "gateDetectorPosition", "cabsimType"
)

_debug = False
def _dprint(*args):
    if(_debug):
        print(*args)

class Preset:

    def __init__(self, load_file):
        self.preset_dict = json.load(open(load_file))
        self.node_dict = {}
        for node in self.preset_dict["audioGraph"]["nodes"]:
            self.node_dict[node["nodeId"]] = node

    def get_product_id(self):
        return self.preset_dict["info"]["product_id"]

    def uiparams(self, node_order = _DSP_UNIT_TYPES):
        print(f"UI params for preset {self.preset_dict["info"]["displayName"]}")
        print(f"Source product id: {self.preset_dict["info"]["product_id"]}")
        for which_node_id in node_order:
            node = self.node_dict[which_node_id]
            fid = node["FenderId"]
            if fid in ( "DUBS_Passthru", ):
                print(f"{which_node_id}: None")
            else:
                stripped_fid = strip_prefixes_and_suffixes(fid)
                preset_params = node["dspUnitParameters"]
                dsp_unit = dspunit_for_name(which_node_id, stripped_fid, preset_params)
                if dsp_unit is None:
                    print(f"DSP unit {stripped_fid} not found", file=sys.stderr)
                    continue
                print(f"{which_node_id}: {dsp_unit.displayName()} {dsp_unit.render_params(preset_params)}")


class DspUnit:

    def __init__(self, load_file):
        self.dspunit_dict = json.load(open(load_file))
        self.param_dict = {}
        for param in self.dspunit_dict["ui"]["uiParameters"]:
            self.param_dict[param["controlId"]]=param

    def displayName(self):
        return self.dspunit_dict["info"]["audioGuiObjectNameMaximized"]

    def get_ui_metadata(self, param_id):
        return self.param_dict.get(param_id, { "paramGuiObjectNameMinimized": param_id})

    def render_params(self, preset_param_dict):
        param_items = []
        for k in sorted(preset_param_dict.keys()):
            if k in _PARAMS_TO_IGNORE:
                continue
            ui_metadata = self.get_ui_metadata(k)
            display_key = ui_metadata["paramGuiObjectNameMaximized"]
            param_items += [ f"{display_key}:{preset_param_dict[k]}"]
        return "(" + ", ".join(param_items) + ")"


def preset_for_name(preset_name):
    preset = None
    for candidate_basename in os.listdir(_DATA_DIR):
        if candidate_basename.startswith(f"preset-{preset_name}"):
            preset = Preset(os.path.join(_DATA_DIR, candidate_basename))
            if preset.get_product_id() != "mustang-lt":
                # probably a Rumble LT25 preset - presently not supported
                continue
            else:
                _dprint(f"Loaded preset {preset_name} from {candidate_basename}")
                return preset

def dspunit_for_name(dsp_unit_type, dsp_unit_name, preset_params):
    dsp_unit = None
    for candidate_basename in reversed(sorted(os.listdir(_DATA_DIR))):
        if dsp_unit_name + "." in candidate_basename:
            dsp_unit = DspUnit(os.path.join(_DATA_DIR, candidate_basename))
            _dprint(f"Loaded DSP unit {dsp_unit_name} from {candidate_basename}")
            preset_param_keys = [
                k
                for k in preset_params.keys()
                if k not in _PARAMS_TO_IGNORE
            ]
            dspunit_param_keys = [
                k
                for k in dsp_unit.dspunit_dict["defaultDspUnitParameters"].keys()
                if k not in _PARAMS_TO_IGNORE
            ]
            _dprint(f"preset_params: {preset_param_keys}")
            _dprint(f"candidate_params: {dspunit_param_keys}")
            if preset_param_keys != dspunit_param_keys:
                continue
            return dsp_unit

def strip_prefixes_and_suffixes(fender_id):
    retval = fender_id
    for p_or_s in ( "DUBS_", "ACD_", "GT", "Reverb", "Lite" ):
        retval = retval.replace(p_or_s,"")
    return retval


if __name__ == "__main__":
    for name in (
        "VINTAGE",
        # "THRASH",
        "CHICAGO",
        "60S_____FUZZ"
    ):
        try:
            preset = preset_for_name(name)
            if preset is None:
                continue
            preset.uiparams()
        except:
            print(f"Unable to process {name}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
        print()



