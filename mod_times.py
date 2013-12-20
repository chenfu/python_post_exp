'''
This is one module to get experiment start time and end time in trace_log file.


Fu Chen, 4/11/2013
'''

import sys, re, os

# The base class for all operations
class Operation(object):
    """The base class for all operation classes"""
    def __init__(self, parser_name):
        self.data = {}
        self.types = {0: (parser_name + '_All_types', 'None')}
        self.cur_type = 0 # This is current chosen type. 0 means all types.
    
    # Iteration functions for easily data accessing
    def __iter__(self):
        #Obtain the key list and reset start point:
        self.key_list = sorted(self.data.keys())
        self.index = -1
        return self
    
    # Return time and its operation type value (always 0 here)
    # if no types are chosen, return (time, sum_type, num)
    # if a specific type is given, return (time, num)
    def next(self):
        if self.index >= len(self.key_list) -1:
            raise StopIteration
        self.index = self.index + 1
        
        if self.cur_type == 0:
            sum_type = 0
            sum_num = 0
            for type_code in sorted(self.types.keys()):
                if type_code == 0:
                    continue
                if type_code in self.data[self.key_list[self.index]]:
                    sum_type = sum_type + type_code
                    sum_num = sum_num + self.data[self.key_list[self.index]][type_code]
            return (self.key_list[self.index], sum_type, sum_num)
        else:
            while not self.cur_type in self.data[self.key_list[self.index]]:
                if self.index >= len(self.key_list) -1:
                    raise StopIteration
                self.index = self.index + 1
            return (self.key_list[self.index],
                    self.data[self.key_list[self.index]][self.cur_type])
        
        
#        return (self.key_list[self.index], self.data[self.key_list[self.index]][0])
    
    # Denotes a specific output operation type in iterator
    #  0: means all types are chosen
    def choose_type(self, type_code):
        if type_code in self.types:
            self.cur_type = type_code
        else:
            print type_code, 'is a unrecognised type code'
            print 'current type is still', self.types[self.cur_type][0]
            sys.exit(2)
    
    # Get the description string for a specific operation type
    def cur_type_str(self):
        return self.types[self.cur_type][0]
    
    # Parse string to fill data records according to different data types 
    #  stored in self.types
    def parse(self, line_string):
        for index in self.types.keys():
            if index == 0:
                continue
            pat = re.compile(self.types[index][1])
            m = pat.match(line_string)
            if m:
                time_p = int(m.group(1))
                if time_p in self.data:
                    if index in self.data[time_p]:
                        self.data[time_p][index] = self.data[time_p][index] + 1
                    else:
                        self.data[time_p][index] = 1
                else:
                    self.data[time_p] = {index:1}
                
                break
    
    # Save collected data to file
    def save_to_file(self, save_dir):
        for op in self.types.keys():
            if op == 0:
                continue
            self.choose_type(op)
            print "-- Writing to file:", self.cur_type_str()
            save_file = save_dir + os.sep + self.cur_type_str()
            with open(save_file, 'w') as save_f:
                save_f.writelines(['Time\t', self.cur_type_str(), '\n'])
                for time, op_num in self:
                    save_f.writelines([str(time), '\t', str(op_num), '\n'])


# This is the class for operations with a value (ONLY ONE value is allowed now)
class ValueOperation(Operation):
    """The base class for operations with value. This derived from Operation"""
    def __init__(self, parser_name):
        super(ValueOperation, self).__init__(parser_name)
    
    # Return time and its operation type value (always 0 here)
    # if no types are chosen, return (time, sum_type, num, ave_value)
    # if a specific type is given, return (time, num, ave_value)
    # !!! --- evaluate the average value for each type of data --- !!!
    def next(self):
        if self.index >= len(self.key_list) -1:
            raise StopIteration
        self.index = self.index + 1
        
        if self.cur_type == 0:
            sum_type = 0
            sum_num = 0
            sum_ave_value = 0
            for type_code in sorted(self.types.keys()):
                if type_code == 0:
                    continue
                if type_code in self.data[self.key_list[self.index]]:
                    num = len(self.data[self.key_list[self.index]][type_code])
                    sum_type = sum_type + type_code
                    sum_num = sum_num + num
                    ave_value = float(sum(self.data[self.key_list[self.index]][type_code])) / float(num)
                    sum_ave_value = sum_ave_value + ave_value
            return (self.key_list[self.index], sum_type, sum_num, sum_ave_value)
        else:
            while not self.cur_type in self.data[self.key_list[self.index]]:
                if self.index >= len(self.key_list) -1:
                    raise StopIteration
                self.index = self.index + 1
            num = len(self.data[self.key_list[self.index]][self.cur_type])
            op_sum = sum(self.data[self.key_list[self.index]][self.cur_type])
            return (self.key_list[self.index], num, float(op_sum)/float(num))
        
        
#        return (self.key_list[self.index], self.data[self.key_list[self.index]][0])
    
    # Parse string to fill data records according to different data types 
    #  stored in self.types
    def parse(self, line_string):
        for index in self.types.keys():
            if index == 0:
                continue
            pat = re.compile(self.types[index][1])
            m = pat.match(line_string)
            if m:
                time_p = int(m.group(1))
                op_value = int(m.group(2))
                if time_p in self.data:
                    if index in self.data[time_p]:
                        self.data[time_p][index].append(op_value)
                    else:
                        self.data[time_p][index] = [op_value]
                else:
                    self.data[time_p] = {index:[op_value]}
                
                break
    # Overwite the save_to_file in the parent class
    def save_to_file(self, save_dir):
        for op in self.types.keys():
            if op == 0:
                continue
            self.choose_type(op)
            print "-- Writing to file:", self.cur_type_str()
            save_file = save_dir + os.sep + self.cur_type_str()
            with open(save_file, 'w') as save_f:
                save_f.writelines(['Time\t', self.cur_type_str(), '\n'])
                for time, op_num, op_value in self:
                    save_f.writelines([str(time), '\t', str(op_num), '\t', '%.2f' % op_value, '\n'])

# The parser classes decleared from here:
class FingerTable(Operation):
    """A class to record finger table related operations"""
    def __init__(self):
        super(FingerTable, self).__init__('FingerTable') # This invokes its parent's con.
        self.types.update({ 
            1:('Finger_Insert', '^(\d+)\.\d+ finger_table: [0-9A-Fa-f]+: stabilize_finger: findsucc of finger \d+'),
            2:('Finger_Fix', '^(\d+)\.\d+ finger_table: [0-9A-Fa-f]+: stabilize_finger_getpred_cb: fixing finger \d+')
        })
    

class DhashBlock(ValueOperation):
    """A Class to record dhash block store operations""" #Here for store only, fetch will be added later
    def __init__(self):
        super(DhashBlock, self).__init__('DHash_Block_lat')
        self.types.update({
            1:('DHash_Succ_Store', '^(\d+)\.\d+ dhashcli: store [0-9A-Fa-f]+ \(frag \d+/\d+\) -> [0-9A-Fa-f]+ in (\d+)ms: DHASH_OK'), 
            2:('DHash_TO_Store', '^(\d+)\.\d+ dhashcli: store [0-9A-Fa-f]+ \(frag \d+/\d+\) -> [0-9A-Fa-f]+ in (\d+)ms: DHASH_TIMEOUT')
        })
    