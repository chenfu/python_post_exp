'''
This script contains all utilies for old experiment result processing

Fu Chen 14/12/2013
'''
import re

from pandas import Series

# This function finds all operation's instruction of all experiment machines with
#  their count number.
#
# Output the list of (operation, instruction, count)

def get_stages(file_name):
    instruction_pat = re.compile('(Insert|Fetch) Instruction:(.+)')
    
    counts = {} #Number of each operation's instruction in settings file (OLD)
    
    # Read through the setting file:
    for line in (open(file_name)):
        instruction_mat = instruction_pat.search(line)
        if instruction_mat:
            op = instruction_mat.group(1)
            inst = instruction_mat.group(2).strip(' \t\n\r')
            
            if op in counts:
                if inst in counts[op]:
                    counts[op][inst] = counts[op][inst] + 1
                else:
                    counts[op][inst] = 0
            else:
                counts[op] = {}
    
    ret = []
    
    for op_k, op_v in counts.iteritems():
        for inst_k, inst_v in op_v.iteritems():
            ret.append((op_k, inst_k, inst_v))
    
    return ret
