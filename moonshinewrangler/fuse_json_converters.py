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

default_param_converters = [
    pc_volume, pc_gain,
    pc_treble, pc_mid, pc_bass,
    pc_presence
]

ModuleConverter = namedtuple("ModuleConverter", "fuse_type fuse_id json_id param_converters")

_MODULE_CONVERTERS = (
    ModuleConverter("Amplifier", 117, 'Twin57', default_param_converters),
)


def fuse_mc_lookup(fuse_module_id):
    matching_mcs = [
        mc
        for mc in _MODULE_CONVERTERS
        if mc.fuse_id == fuse_module_id
    ]
    assert len(matching_mcs) == 1
    return matching_mcs[0]


if __name__ == "__main__":

    import sys
    import xml.etree.ElementTree as ET
    import zipfile

    with zipfile.ZipFile("./_work/reference_files/intheblues.zip") as zf:
        # print("\n".join(zf.namelist()))
        with zf.open("intheblues/mustangv2mark-knopfler.fuse") as mk_stream:
            preset_tree = ET.ElementTree(
                ET.fromstring(str(mk_stream.read(), "utf-8"))
            )
            print(preset_tree)
            preset_tree.write(sys.stdout, "unicode")

            fuse_amp_element = preset_tree.getroot()[0]
            assert fuse_amp_element.tag == "Amplifier"
            ui_params = {}
            json_amp_dict = {}
            mc = fuse_mc_lookup(int(fuse_amp_element[0].attrib.get("ID")))
            json_amp_dict["FenderId"] = mc.json_id
            for param in fuse_amp_element.items():
                pass
