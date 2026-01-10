from generated import classic_modules

_FDM = classic_modules.FUSE_DSP_MODULES

class SourceFilePatcher:

    def __init__(self, target_path):
        self.target_path = target_path
        self.target_lines = open(target_path, "rt").readlines()

    def patch(self, region_label, item_list, item_line_lambda):
          ( region_start_line, ) = [
                line_no 
                for line_no in range(0,len(self.target_lines))
                if f"{region_label} generated entries begin" in self.target_lines[line_no]
          ]
          ( region_end_line, ) = [
                line_no 
                for line_no in range(0,len(self.target_lines))
                if f"{region_label} generated entries end" in self.target_lines[line_no]
          ]
          lines_before_insertion = self.target_lines[0:region_start_line+1]
          insertion_lines = [ item_line_lambda(item) for item in item_list ]
          lines_after_insertion = self.target_lines[region_end_line:]
          print([
                len(lines)
                for lines in (
                     lines_before_insertion, insertion_lines, lines_after_insertion,  
                )
            ])
          self.target_lines = lines_before_insertion + insertion_lines + lines_after_insertion

    def write(self):
          open(self.target_path,"wt").writelines(self.target_lines)
          
if __name__ == "__main__":
        
        patcher1 = SourceFilePatcher('../maneline/maneline-lib/src/main/java/net/heretical_camelid/maneline/lib/generated/FUSE_Constants.java')
        items1 = sorted(_FDM.keys())
        lambda1 = lambda id: f'        registerModule({id}, "{_FDM[id][1]}", "{_FDM[id][0]}");\n'
        patcher1.patch('registerModule',items1,lambda1)
        patcher1.write();









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