from generated import classic_modules

_FDM = classic_modules.FUSE_DSP_MODULES

if __name__ == "__main__":
        template_file = open("moonshinewrangler/templates/FUSE_Classic_Preset.java.template","rt")
        template_text = template_file.read()
        # TODO mungle template_text
        java_file=open("../maneline/maneline-lib/src/main/java/net/heretical_camelid/maneline/lib/generated/FUSE_Classic_Preset.java", "wt")
        print(template_text,file=java_file);









"""    try:
        java_file.writelines([
            "package net.maneline.lib.generated;\n"
            "import net.maneline.lib.fuse.FUSE_DSP_Module;\n"
            "FUSE_DSP_MODULES = {\n",
        ])
        for k in sorted(dsp_ids_to_types_and_names):
            v = dsp_ids_to_types_and_names[k]
            java_file.writelines([f'    {k:3d}: new FUSE_DSP_Module({k},"{v[0]}","{v[1]}"),\n'])
        java_file.writelines(["}\n"])        
    except FileNotFoundError:
        pass
"""