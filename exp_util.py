# -*- coding: utf-8 -*-
'''
This script contains all utilies for experiment result processing

Fu Chen 13/12/2013
'''
import re, os

from pandas import Series

# Start searching for each machine's target file recursively
# return: none if can't find OR the full path of the one found file
def find_target(cur_dir, target_file):
    #print "*** Finding in", cur_dir
    
    for dir_entry in os.listdir(cur_dir):
        abs_path = cur_dir + os.sep + dir_entry
        #print "*** Checking", dir_entry, "::", abs_path
        if dir_entry == target_file:
            #print "*** Found one", abs_path
            return abs_path
        elif os.path.isdir(abs_path):
            #print "*** Go Deeper", abs_path
            ret = find_target(abs_path, target_file)
            if ret != None:
                return ret
    return None

# This is the class to update experiment earliest start time and latest end time
class exp_time(object):
    def __init__(self):
        self.start_time = 0
        self.end_time = 0
    
    def parse_time(self, line_string):
        start_pat = re.compile('^(\d+)\.\d+ lsd: starting: .+')
        end_pat = re.compile('^(\d+)\.\d+ lsd: stopping.')
    
        m_start = start_pat.match(line_string)
        if m_start:
            cur_start_time = int(m_start.group(1))
            if self.start_time == 0 or cur_start_time < self.start_time:
                self.start_time = cur_start_time
            return
    
        m_end = end_pat.match(line_string)
        if m_end:
            cur_end_time = int(m_end.group(1))
            if cur_end_time > self.end_time:
                self.end_time = cur_end_time
    
    # Get (earliest_start, latest_end) experiment times
    def get_times(self):
        return (self.start_time, self.end_time)
    
    # Save the earliest_start and latest_time into a file in a given directory
    def save_times(self, save_dir):
        if not os.path.isdir(save_dir):
            print 'Cannot find save directory:', save_dir
            return
        
        save_file = save_dir + os.sep + 'time'
        with open(save_file, 'w') as save_f:
            save_f.writelines([str(self.start_time), '\n', str(self.end_time)])

# This function finds through an experiment setting file and find out 
#  all experiment stages.
#
# Output the list of (start, end) of each experiment stage.

def get_stages(file_name):
    time_pat = re.compile('TIMES:(\d+)\.\d+-(\d+)\.\d+')
    instruction_pat = re.compile('(\w+)_instruction:(.+)')
    
    start_time = 0
    
    start_tp = {}
    end_tp = {}
    
    labels = {} #It has operation name with their start time and end time
    
    tags = {'insert':1, 'fetch':2}
    
    counts = {} #It has number of time labels for each operation
    
    # Read through the setting file:
    for line in (open(file_name)):
        time_mat = time_pat.search(line)
        if time_mat:
            start_time = int(time_mat.group(1))
            end_time = int(time_mat.group(2))
            
            start_tp[start_time] = 0
            end_tp[end_time] = 0
            
            continue
        
        instruction_mat = instruction_pat.search(line)
        if instruction_mat:
            print 'Found:', instruction_mat.group(2)
            time_list = re.findall('(\d+):(\d+);', instruction_mat.group(2))
            if len(time_list) == 0:
                continue
            elif start_time == 0:
                print 'Cannot find experiment start time'
                return []
            else:
                first = 0
                last = 0
                
                counts[instruction_mat.group(1)] = len(time_list)
                
                for time_p in time_list:
                    cur_time = int(time_p[0])
                    if first == 0:
                        first = cur_time
                    last = cur_time
                    
                    if (cur_time + start_time) in start_tp:
                        start_tp[cur_time + start_time] = start_tp[cur_time + start_time] + tags[instruction_mat.group(1)]
                    else:
                        start_tp[cur_time + start_time] = tags[instruction_mat.group(1)]
                    end_tp[cur_time + start_time -1] = 0
                    
                    labels[instruction_mat.group(1)] = (first, last)
    
    # Convert to dateIndex
    start_tm_index = Series(start_tp)
    start_tm_index.index = start_tm_index.index.astype('datetime64[s]')
    start_tm_index.index = start_tm_index.index.tz_localize('UTC')
    start_tm_index.index = start_tm_index.index.tz_convert('Europe/London')
    #start_tm_index = start_tm_index.index
    
    end_tm_index = Series(end_tp)
    end_tm_index.index = end_tm_index.index.astype('datetime64[s]')
    end_tm_index.index = end_tm_index.index.tz_localize('UTC')
    end_tm_index.index = end_tm_index.index.tz_convert('Europe/London')
    end_tm_index = end_tm_index.index
    
    time_bound = [] # (start_point, end_point) are stored in this list
    
    for index_t in range(len(start_tm_index)):
        time_bound.append((start_tm_index.index[index_t], end_tm_index[index_t], start_tm_index[index_t]))
    
    return time_bound
