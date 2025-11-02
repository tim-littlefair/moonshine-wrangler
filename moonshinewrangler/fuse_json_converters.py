# python3
# fuse_vs_json.py
# Author: Tim Littlefair, October 2025-

# Structures to help translation back and forth between
# the XML-based format used by the Fender FUSE software for Mustang V2 amps
# and the JSON-based format used by the Fender Tone software Mustang LT-
# and Mustang Micro Plus amps (possibly also Mustang GT- and GTX- series
# but I don't have access to any of those at present).

from collections import namedtuple

from fuse_json_adaptors import ContinuousValuedParameterAdaptor as CVPA
from fuse_json_adaptors import StringChoiceParameterAdaptor as SCPA


ParamConverter = namedtuple("ParamConverter", "fuse_param_id fuse_module_id json_param_name json_module_id ui_param_name parameter_adaptor")

default_cvpa = CVPA()
pc_volume = ParamConverter(0, None, "volume", None, "VOLUME", default_cvpa)
pc_gain = ParamConverter(1, None, "gain", None, "GAIN", default_cvpa)
# FUSE params 2 and 3 are called GAIN2 and MASTER VOLUME
# Neither appears to be used for JSON
pc_treble = ParamConverter(4, None, "treble", None, "TREBLE", default_cvpa)
pc_mid = ParamConverter(5, None, "mid", None, "MIDDLE", default_cvpa)
pc_bass = ParamConverter(6, None, "bass", None, "BASS", default_cvpa)
pc_presence = ParamConverter(7, None, "presence", None, "PRESENCE", default_cvpa)

_DEFAULT_AMP_PARAM_CONVERTERS = (
    pc_volume, pc_gain,
    pc_treble, pc_mid, pc_bass,
    pc_presence,
)

pc_level = ParamConverter(0, None, "level", None, "LEVEL", default_cvpa)
pc_decay = ParamConverter(1, None, "decay", None, "DECAY", default_cvpa)
pc_dwell = ParamConverter(2, None, "dwell", None, "DWELL", default_cvpa)
pc_diffusion = ParamConverter(3, None, "diffusion", None, "DIFFUSION", default_cvpa)
pc_tone = ParamConverter(4, None, "Tone", None, "TONE", default_cvpa)

_DEFAULT_REVERB_PARAM_CONVERTERS = (
    pc_level, pc_decay, pc_dwell,
    pc_diffusion, pc_tone,
)

low_med_hi_max_pa = SCPA(
    ["low", "medium", "high", "super"],
    {"low": "LOW", "medium": "MID", "high": "HIGH", "super": "MAX"}
)

pc_compressor_type = ParamConverter(5, None, "type", None, "TYPE", low_med_hi_max_pa)

ModuleConverter = namedtuple("ModuleConverter", "fuse_type fuse_id json_id ui_name param_converters")

_MODULE_CONVERTERS = (
    ModuleConverter("Amplifier", 117, "Twin65", "TWIN CLEAN", _DEFAULT_AMP_PARAM_CONVERTERS),
    ModuleConverter("Effect", 0, "Passthru", "EMPTY", ()),
    ModuleConverter("Effect", 58, "LargeHall", "LARGE HALL", _DEFAULT_REVERB_PARAM_CONVERTERS),
    ModuleConverter("Effect", 136, "SimpleCompressor", "COMPRESSOR", (pc_compressor_type,))
)


def fuse_mc_lookup(fuse_module_id):
    matching_mcs = [
        mc
        for mc in _MODULE_CONVERTERS
        if mc.fuse_id == fuse_module_id
    ]
    assert len(matching_mcs) == 1, f"Converter not found for module {fuse_module_id}"
    return matching_mcs[0]


def fuse_pc_lookup(mc, fuse_param_id):
    matching_pcs = [
        pc
        for pc in mc.param_converters
        if pc.fuse_param_id == fuse_param_id
    ]
    assert len(matching_pcs) <= 1
    if len(matching_pcs) == 1:
        return matching_pcs[0]
    else:
        return None


def convert_fuse_module(fuse_amp_element):
    mc = fuse_mc_lookup(int(fuse_amp_element[0].attrib.get("ID")))
    json_params = {}
    ui_params = {}
    for fuse_param_element in fuse_amp_element[0]:
        pc = fuse_pc_lookup(mc, int(fuse_param_element.attrib.get("ControlIndex")))
        if pc is not None:
            json_name = pc.json_param_name
            json_value = pc.parameter_adaptor.fuse_to_json.adapt(
                        int(fuse_param_element.text)
                    )
            json_params[json_name] = json_value
            ui_name = pc.ui_param_name
            ui_value = pc.parameter_adaptor.json_to_ui.adapt(
                        json_value
                    )
            ui_params[ui_name] = ui_value
        else:
            fuse_ci = fuse_param_element.attrib.get("ControlIndex")
            json_params["__"+fuse_ci] = fuse_param_element.text
    return (
        {"FenderId": mc.json_id, "dspUnitParameters": json_params},
        {mc.ui_name: ui_params}
    )


if __name__ == "__main__":

    import json
    import sys
    import traceback
    import xml.etree.ElementTree as ET
    import zipfile

    with zipfile.ZipFile("./_work/reference_files/intheblues.zip") as zf:
        # print("\n".join(zf.namelist()))
        with zf.open("intheblues/mustangv2mark-knopfler.fuse") as mk_stream:
            preset_tree = ET.ElementTree(
                ET.fromstring(str(mk_stream.read(), "utf-8"))
            )
            ET.indent(preset_tree.getroot())
            preset_tree.write(sys.stdout, "unicode")
            print()

            json_preset_dict = {}
            ui_preset_dict = {}

            fuse_amp_element = preset_tree.getroot()[0]
            assert fuse_amp_element.tag == "Amplifier"

            fuse_stomp_element = preset_tree.getroot()[1][0]
            assert fuse_stomp_element.tag == "Stompbox"

            fuse_mod_element = preset_tree.getroot()[1][1]
            assert fuse_mod_element.tag == "Modulation"

            fuse_delay_element = preset_tree.getroot()[1][2]
            assert fuse_delay_element.tag == "Delay"

            fuse_reverb_element = preset_tree.getroot()[1][3]
            assert fuse_reverb_element.tag == "Reverb"

            json_modules = []
            ui_modules = []
            try:
                for fuse_element in (
                    fuse_stomp_element, fuse_mod_element,
                    fuse_amp_element,
                    fuse_delay_element, fuse_reverb_element
                ):
                    j, u = convert_fuse_module(fuse_element)
                    json_modules += [j]
                    ui_modules += [u]
            except RuntimeError:
                traceback.print_exception()
                print("Partial results:")
            print(json.dumps(json_modules, indent=4))
            print(json.dumps(ui_modules, indent=4))
