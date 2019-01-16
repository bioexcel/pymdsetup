#!/usr/bin/env python

"""Python module to generate a restrained topology from an index file
"""
import sys
import json
import configuration.settings as settings
from tools import file_utils as fu
import shutil as su
import os
import fnmatch


class Ndx2resttop(object):
    """Generate a restrained topology from an index file.
    Args:
        input_ndx_path (str): Path to the input NDX index file.
        input_top_zip_path (str): Path the input TOP topology in zip format.
        output_top_zip_path (str): Path the output TOP topology in zip format.
        properties (dic):
            output_top_path (str): Path the output TOP file.
            force_constants (float[3]): Array of three floats defining the force constants.
            ref_rest_chain_triplet_list (str): Triplet list composed by (reference group, restrain group, chain) list.
            group (str): Group of the index file where the restrain will be applied.
    """

    def __init__(self, input_ndx_path, input_top_zip_path,
                 output_top_zip_path, properties, **kwargs):

        self.input_ndx_path = input_ndx_path
        self.input_top_zip_path = input_top_zip_path
        self.output_top_zip_path = output_top_zip_path
        self.output_top_path = properties.get('output_top_path','restrain.top')
        self.force_constants = properties.get('force_constants','500 500 500')
        self.ref_rest_chain_triplet_list = properties.get('ref_rest_chain_triplet_list', None)
        self.mutation = properties.get('mutation',None)
        self.step = properties.get('step',None)
        self.path = properties.get('path','')

    def launch(self):
        """Launch the topology generation.
        """
        out_log, err_log = fu.get_logs(path=self.path, mutation=self.mutation, step=self.step)
        self.output_top_path = fu.add_step_mutation_path_to_name(self.output_top_path, self.step, self.mutation)

        top_path = fu.unzip_top(zip_file=self.input_top_zip_path, top_file=self.output_top_path, dest_dir=self.mutation+'_'+self.step+'_top', out_log=out_log)
        out_log.info('Unzip: '+ self.input_top_zip_path + ' to: '+top_path)

        # Create index list of index file :)
        index_dic={}
        out_log.info('1')
        lines = open(self.input_ndx_path, 'r').read().splitlines()
        out_log.info(lines)
        out_log.info('2')
        for index, line in enumerate(lines):
            if line.startswith('['):
                index_dic[line] = index,
                if index > 0:
                    index_dic[label] = index_dic[label][0], index
                label = line
        index_dic[label] = index_dic[label][0], index
        out_log.info('Index_dic: '+str(index_dic))

        self.ref_rest_chain_triplet_list = [tuple(elem.strip(' ()').replace(' ', '').split(',')) for elem in self.ref_rest_chain_triplet_list.split('),')]
        for reference_group, restrain_group, chain in self.ref_rest_chain_triplet_list:
            out_log.info('Reference group: '+reference_group)
            out_log.info('Restrain group: '+restrain_group)
            out_log.info('Chain: '+chain)
            self.output_itp_path = fu.add_step_mutation_path_to_name(restrain_group+'.itp', self.step, self.mutation)

            # Mapping atoms from absolute enumeration to Chain relative enumeration
            out_log.info('reference_group_index: start_closed:'+str(index_dic['[ '+reference_group+' ]'][0]+1)+' stop_open: '+str(index_dic['[ '+reference_group+' ]'][1]))
            reference_group_list = [ int(elem) for line in lines[index_dic['[ '+reference_group+' ]'][0]+1: index_dic['[ '+reference_group+' ]'][1]] for elem in line.split() ]
            out_log.info('restrain_group_index: start_closed:'+str(index_dic['[ '+restrain_group+' ]'][0]+1)+' stop_open: '+str(index_dic['[ '+restrain_group+' ]'][1]))
            restrain_group_list = [ int(elem) for line in lines[index_dic['[ '+restrain_group+' ]'][0]+1: index_dic['[ '+restrain_group+' ]'][1]] for elem in line.split() ]
            selected_list = [reference_group_list.index(atom)+1 for atom in restrain_group_list]

            # Creating new ITP with restrictions
            with open(self.output_itp_path, 'w') as f:
                out_log.info('Creating: '+str(f)+' and adding the selected atoms force constants')
                f.write('[ position_restraints ]\n')
                f.write('; atom  type      fx      fy      fz\n')
                for atom in selected_list:
                    f.write(str(atom)+'     1  '+self.force_constants+'\n')

            # Including new ITP in the corresponding ITP-chain file
            for file_name in os.listdir('.'):
                if not file_name.startswith("posre") and not file_name.endswith("_pr.itp"):
                    #if fnmatch.fnmatch(file_name, "*_chain_"+chain+".itp"):
                    if fnmatch.fnmatch(file_name,self.mutation+'_'+self.step+"_Protein_chain_"+chain+".itp"):
                        with open(file_name, 'a') as f:
                            out_log.info('Opening: '+str(f)+' and adding the ifdef include statement')
                            f.write('\n')
                            f.write('; Include Position restraint file\n')
                            f.write('#ifdef CUSTOM_POSRES\n')
                            f.write('#include "'+self.output_itp_path+'"\n')
                            f.write('#endif\n')




        # zip topology
        fu.zip_top(top_path, self.output_top_zip_path, remove_files=False, mutation=self.mutation, out_log=out_log)
        out_log.info('Zip: '+ top_path +' to: '+ self.output_top_zip_path)

        return 0
#Creating a main function to be compatible with CWL
def main():
    system=sys.argv[1]
    step=sys.argv[2]
    properties_file=sys.argv[3]
    prop = settings.YamlReader(properties_file, system).get_prop_dic()[step]
    Ndx2resttop(input_ndx_path=sys.argv[4],
                input_top_zip_path=sys.argv[5],
                output_top_zip_path=sys.argv[6],
                properties=prop).launch()

if __name__ == '__main__':
    main()
