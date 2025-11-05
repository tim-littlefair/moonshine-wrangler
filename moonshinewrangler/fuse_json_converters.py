# python3
# fuse_vs_json.py
# Author: Tim Littlefair, October 2025-

# Structures to help translation back and forth between
# the XML-based format used by the Fender FUSE software for Mustang V2 amps
# and the JSON-based format used by the Fender Tone software Mustang LT-
# and Mustang Micro Plus amps (possibly also Mustang GT- and GTX- series
# but I don't have access to any of those at present).

from collections import namedtuple
import traceback

from fuse_json_adaptors import RangeAdaptor as RA
from fuse_json_adaptors import ContinuousValuedParameterAdaptor as CVPA
from fuse_json_adaptors import StringChoiceParameterAdaptor as SCPA
from fuse_json_adaptors import BooleanParameterAdaptor as BPA


ParamConverter = namedtuple("ParamConverter", "Xfuse_param_id json_param_name ui_param_name parameter_adaptor")


def addNewParamConverter(pc_map, fuse_param_id, json_param_name, ui_param_name, ui_param_adaptors):
    new_param_converter = ParamConverter(fuse_param_id, json_param_name, ui_param_name, ui_param_adaptors)
    if pc_map is not None:
        pc_map[fuse_param_id] = new_param_converter
    return new_param_converter


def addParamConverter(pc_map, fuse_param_id, param_converter):
    if pc_map is not None:
        pc_map[fuse_param_id] = param_converter
    return param_converter


default_cvpa = CVPA()

default_bpa = BPA()

volume_cvpa = CVPA(
    # in JSON, volume is represented as a db value between -60.0 and 0.0
    # on the UI's it is represented on the same 1.0-10.0/0%-100% range
    # as the other parameters
    json_min=-60.0, json_max=0.0,
    ui_range_adaptors=(
        RA(
            min_in=-60.0, max_in=0.0,
            min_out=1.0, max_out=10.0,
            format="2.1f", suffix=""
        ),
        RA(
            min_in=-60.0, max_in=0.0,
            min_out=0.0, max_out=100.0,
            format=".0f", suffix="%"
        ),
    )
)

delay_time_cvpa = CVPA(
    # in JSON, volume is represented as a value between 0.03 and 1.5 seconds
    # on the UI's it is represented in milliseconds
    json_min=0.03, json_max=1.5,
    ui_range_adaptors=(
        RA(
            min_in=0.03, max_in=1.5,
            min_out=30, max_out=1500,
            format=".0f", suffix=" ms"
        ),
    )
)

low_med_hi_max_scpa = SCPA(
    ["low", "medium", "high", "super"],
    {"low": "LOW", "medium": "MID", "high": "HIGH", "super": "MAX"}
)


ModuleConverter = namedtuple("ModuleConverter", "fuse_type fuse_id json_id ui_name param_converters")


_MODULE_CONVERTERS = []

# Start of converters for stomp amps

pc_volume = ParamConverter(0, "volume", "VOLUME", volume_cvpa)
pc_gain = ParamConverter(1, "gain", "GAIN", default_cvpa)
# _pc_gain2 = ParamConverter(2, "_gain2", "_GAIN2", default_cvpa)
# _pc_mvol = ParamConverter(3, "_master_volume", "_MASTER_VOLUME", default_cvpa)
pc_treble = ParamConverter(4, "treble", "TREBLE", default_cvpa)
pc_middle = ParamConverter(5, "mid", "MIDDLE", default_cvpa)
pc_bass = ParamConverter(6, "bass", "BASS", default_cvpa)
_pc_presence = ParamConverter(7, "presence", "PRESENCE", default_cvpa)
_pc_resonance = ParamConverter(8, "_resonance", "_RESONANCE", default_cvpa)

_DEFAULT_AMP_PARAM_CONVERTERS = {
    0: pc_volume,
    1: pc_gain,
    4: pc_treble,
    5: pc_middle,
    6: pc_bass,
    7: _pc_presence,
    8: _pc_resonance
}

_MODULE_CONVERTERS += [
    ModuleConverter("Amplifier", 83, "Deluxe65", "DELUXE CLN",  _DEFAULT_AMP_PARAM_CONVERTERS),
    ModuleConverter("Amplifier", 114, "SuperSonic", "BURN", _DEFAULT_AMP_PARAM_CONVERTERS),
    ModuleConverter("Amplifier", 117, "Twin65", "TWIN CLEAN", _DEFAULT_AMP_PARAM_CONVERTERS),
    ModuleConverter("Amplifier", 249, "Ac30Tb", "60S UK CLEAN", _DEFAULT_AMP_PARAM_CONVERTERS),
]

# End of converters for amps

# Start of converters for stomp effects

pc_level = ParamConverter(0, "level", "LEVEL", default_cvpa)
# pc_gain already defined in parameter section for amps
pc_low = ParamConverter(2, "low", "LOW", default_cvpa)
pc_mid = ParamConverter(3, "mid", "MID", default_cvpa)
pc_high = ParamConverter(3, "high", "HIGH", default_cvpa)
pc_compressor_type = ParamConverter(5, "type", "TYPE", low_med_hi_max_scpa)

_OVERDRIVE_PARAM_CONVERTERS = {
    0: pc_level,
    1: pc_level,  # TODO: Fix after refactor complete
    2: pc_low,
    3: pc_mid,   # TODO?: MaybeFix after refactor complete
    4: pc_high
}

_COMPRESSOR_PARAM_CONVERTERS = {
    0: pc_compressor_type
}

_MODULE_CONVERTERS += [
    ModuleConverter("Stompbox", 60, "Overdrive", "OVERDRIVE", _OVERDRIVE_PARAM_CONVERTERS),
    ModuleConverter("Stompbox", 136, "SimpleCompressor", "COMPRESSOR", _COMPRESSOR_PARAM_CONVERTERS),
]

# End of converters for stomp effects

# Start of converters for modulation effects

# pc_level already defined in parameter section for stomp effects
pc_speed = ParamConverter(1, "speed", "SPEED", default_cvpa)
pc_depth = ParamConverter(2, "depth", "DEPTH", default_cvpa)
pc_feedback = ParamConverter(3, "feedback", "FEEDBACK", default_cvpa)
pc_phase = ParamConverter(4, "phase", "PHASE", default_cvpa)
_VIBRATONE_PARAM_CONVERTERS = {
    0: pc_level,
    1: pc_speed,
    2: pc_depth,
    3: pc_feedback,
    4: pc_phase
}

_MODULE_CONVERTERS += [
    ModuleConverter("Modulation", 45, "Vibratone", "VIBRATONE", _VIBRATONE_PARAM_CONVERTERS),
]

# End of converters for modulation effects

# Start of converters for delay effects

# pc_level already defined in section for stomp effects
pc_delay_time = ParamConverter(1, "time", "TIME", delay_time_cvpa)
pc_feedback2 = ParamConverter(2, "feedback", "FEEDBACK", default_cvpa)
pc_brightness3 = ParamConverter(3, "brightness", "BRIGHTNESS", default_cvpa)
pc_attenuation = ParamConverter(4, "attenuation", "ATTENUATION", default_cvpa)
pc_flutter = ParamConverter(3, "flutter", "FLUTTER", default_cvpa)
pc_brightness4 = ParamConverter(4, "brightness", "BRIGHTNESS", default_cvpa)
pc_stereo = ParamConverter(5, "stereo", "STEREO", default_bpa)

_MONO_DELAY_PARAM_CONVERTERS = {
    0: pc_level,
    1: pc_delay_time,
    2: pc_feedback2,
    3: pc_brightness3,
    4: pc_attenuation
}

_TAPE_DELAY_PARAM_CONVERTERS = {
    0: pc_level,
    1: pc_delay_time,
    2: pc_feedback2,
    3: pc_flutter,
    4: pc_brightness4,
    5: pc_stereo
}

_MODULE_CONVERTERS += [
    ModuleConverter("Delay", 22, "MonoDelay", "DELAY", _MONO_DELAY_PARAM_CONVERTERS),
    ModuleConverter("Delay", 43, "TapeDelayLite", "ECHO", _TAPE_DELAY_PARAM_CONVERTERS),
]

# End of converters for delay effects

# Start of converters for reverb effects

# pc_level already defined in section for stomp effects
pc_decay = ParamConverter(1, "decay", "DECAY", default_cvpa)
pc_dwell = ParamConverter(2, "dwell", "DWELL", default_cvpa)
pc_diffusion = ParamConverter(3, "diffuse", "DIFFUSE", default_cvpa)
pc_tone = ParamConverter(4, "tone", "TONE", default_cvpa)

_DEFAULT_REVERB_PARAM_CONVERTERS = {
    0: pc_level,
    1: pc_decay,
    2: pc_dwell,
    3: pc_diffusion,
    4: pc_tone,
}

_MODULE_CONVERTERS += [
    ModuleConverter("Reverb", 11, "Spring65", "SPRING 65", _DEFAULT_REVERB_PARAM_CONVERTERS),
    ModuleConverter("Reverb", 58, "LargeHall", "LARGE HALL", _DEFAULT_REVERB_PARAM_CONVERTERS),
]

# End of converters for reverb effects

_MODULE_CONVERTERS += [
    ModuleConverter(None, 0, "Passthru", "NONE", ()),
]


def fuse_mc_lookup(fuse_module_type, fuse_module_id):
    matching_mcs = [
        mc
        for mc in _MODULE_CONVERTERS
        if (
            (mc.fuse_id == fuse_module_id) and
            (
                (mc.fuse_type is None) or
                (mc.fuse_type == fuse_module_type)
            )
        )
    ]
    assert len(matching_mcs) == 1, f"Converter not found for {fuse_module_type} {fuse_module_id}"
    return matching_mcs[0]


def fuse_pc_lookup(mc, fuse_param_id):
    if isinstance(mc.param_converters, dict):
        return mc.param_converters.get(fuse_param_id, None)
    matching_pcs = [
        pc
        for pc in mc.param_converters
        if pc.Xfuse_param_id == fuse_param_id
    ]
    assert len(matching_pcs) <= 1
    if len(matching_pcs) == 1:
        return matching_pcs[0]
    else:
        return None


def convert_fuse_module(
    fuse_module_type, fuse_module_element,
    unconverted_param_values
):
    mc = fuse_mc_lookup(
        fuse_module_type,
        int(fuse_module_element[0].attrib.get("ID"))
    )
    json_params = {}
    ui_params = {}
    for fuse_param_element in fuse_module_element[0]:
        fuse_param_id = int(fuse_param_element.attrib.get("ControlIndex"))
        try:
            pc = fuse_pc_lookup(mc, fuse_param_id)
            if pc is not None:
                json_name = pc.json_param_name
                adapted_value = pc.parameter_adaptor.fuse_to_json(
                    int(fuse_param_element.text)
                )
                if adapted_value is None:
                    print(f"Failed to adapt {pc} from value {fuse_param_element.text}")
                    continue
                json_params[json_name] = adapted_value
                ui_name = pc.ui_param_name
                ui_value = pc.parameter_adaptor.json_to_ui(adapted_value)
                ui_params[ui_name] = ui_value
            else:
                json_params["__"+str(fuse_param_id)] = fuse_param_element.text
                if unconverted_param_values is not None:
                    upv_key = (mc.fuse_type, fuse_param_id, int(fuse_param_element.text))
                    upv_entry = unconverted_param_values.get(upv_key, [0, {}])
                    upv_module_count = upv_entry[1].get(mc.fuse_id, 0)
                    upv_entry[1][mc.fuse_id] = upv_module_count + 1
                    upv_entry[0] = sum(upv_entry[1].values())
                    unconverted_param_values[upv_key] = upv_entry
        except Exception as e:
            message = f"Attempting to process {mc.fuse_type} {mc.fuse_id} param {fuse_param_id}"
            traceback.print_exception(e)
            print(message)
            raise RuntimeError(message)

    return (
        {"FenderId": mc.json_id, "dspUnitParameters": json_params},
        {"module_type": mc.fuse_type, "module_name": mc.ui_name, "params": ui_params}
    )


def fuse_to_json(
    mk_stream,
    xml_stream=None,
    unconverted_param_values=None
):
    problems = []
    json_modules = []
    ui_modules = []
    try:
        preset_tree = ET.ElementTree(
            ET.fromstring(str(mk_stream.read(), "utf-8"))
        )
        ET.indent(preset_tree.getroot())
        if xml_stream is not None:
            preset_tree.write(xml_stream, "unicode")

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

        for fuse_element in (
            fuse_amp_element,
            fuse_stomp_element, fuse_mod_element,
            fuse_amp_element,
            fuse_delay_element, fuse_reverb_element
        ):
            try:
                j, u = convert_fuse_module(
                    fuse_element.tag, fuse_element,
                    unconverted_param_values
                )
                json_modules += [j]
                ui_modules += [u]
            except AssertionError as e:
                problems += [str(e)]
            except Exception as e:
                problem = str(e)
                if problem in problems:
                    # duplicate
                    pass
                else:
                    problems += [problem]
    except Exception as e:
        problem = str(e)
        if problem in problems:
            # duplicate
            pass
        else:
            problems += [problem]

    return problems, json_modules, ui_modules


if __name__ == "__main__":

    import json
    import os
    import xml.etree.ElementTree as ET
    import zipfile

    which_zf = "intheblues"
    with zipfile.ZipFile(f"./_work/reference_files/{which_zf}.zip") as zf:
        outdir = f"output/{which_zf}"
        os.makedirs(outdir, exist_ok=True)
        ui_params_stream = open(f"{outdir}/_ui_params.txt", "wt")
        failures_stream = open(f"{outdir}/_failures.txt", "wt")
        unconverted_param_values = {}

        for fn in [
            n
            for n in zf.namelist()
            if not n.startswith("__MACOSX") and n.endswith(".fuse")
        ]:
            output_fn = f"{outdir}/{os.path.basename(fn)}"
            failed_modules, json_modules, ui_modules = fuse_to_json(
                zf.open(fn), open(output_fn, "wt"),
                unconverted_param_values
            )
            if len(failed_modules) == 0:
                output_fn = output_fn.replace(".fuse", ".json")
                print(json.dumps([json_modules[i] for i in [1, 2, 3, 4, 5]], indent=4), file=open(output_fn, "wt"))
                print(f"\nUI parameters for {fn}", file=ui_params_stream)
                for module in [ui_modules[i] for i in [0, 1, 2, 4, 5]]:
                    assert len(module.keys()) == 3
                    if module["module_type"] is not None:
                        print(
                            f"{module["module_type"]}: {module["module_name"]} {module["params"] or ""}",
                            file=ui_params_stream
                        )
                print(f"Exported {output_fn}")
            else:
                print(
                    f"Failed to find one or more modules for {fn}\n{"\n".join(failed_modules)}",
                    file=failures_stream
                )
                print(file=failures_stream)
        unconverted_params_stream = open(f"{outdir}/_unconverted_params.txt", "wt")
        for k in sorted(unconverted_param_values.keys()):
            print(k, unconverted_param_values[k], file=unconverted_params_stream)
