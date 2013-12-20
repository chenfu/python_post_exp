#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This is the trace_log file engine used to organise the modules of info extraction.

Input: trace_log file
Output: operation_num and operation value. Each operation has a separated output
        file.

Fu Chen, 3/11/2013
'''

import sys, getopt, os

import exp_util, mod_times

# This is the working direcoty, and trace_log file
working_dir = None
target_file = None

# This is the output directory
output_dir = None

def parse_arg(argv):
    global working_dir
    global target_file
    global output_dir
	
    try:
        opts, args = getopt.getopt(argv, "hw:t:o:", ["wdir=", "target=", "odir="])
    except getopt.GetoptError:
        print 'trace_engine.py -w <working_dir> -t <target> -o <output_dir>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'trace_engine.py -w <working_dir> -t <target> -o <output_dir>'
            sys.exit(2)
        elif opt == '-w':
            working_dir = os.path.dirname(arg)
        elif opt == '-t':
            target_file = arg
        elif opt == '-o':
            output_dir = arg

# Getting arguments and check arguments
if __name__ == "__main__":
    parse_arg(sys.argv[1:])
    if working_dir == None:
        print '!! Please provide working directory'
        sys.exit(2)
    elif target_file == None:
        print '!! Please provide target file'
        sys.exit(2)
    elif output_dir == None:
        print '!! Please provide output directory name'
        sys.exit(2)
    
    if not os.path.isdir(working_dir):
        print '!! Working directory:', working_dir, 'does not exist'
        sys.exit(2)
    output_dir = working_dir + os.sep + output_dir
    
    if not os.path.exists(output_dir):
        try:
            os.mkdir(output_dir)
        except OSError as e:
            print e.strerror
    elif not os.path.isdir(output_dir):
        print '!! Output directory cannot be created due to a file has the same name in:', working_dir
    else:
        print '!! The output directory has already existed:', output_dir
#        sys.exit(2)

'''
print "Working directory is: ", working_dir
print "Target file is: ", target_file
print "Output directory is: ", output_dir
'''

# Start and end time （earliest start time and latest end time)
time_proc = exp_util.exp_time()

# All parser objects are declared from here:
finger_parser = mod_times.FingerTable()
dblock_lat_parser = mod_times.DhashBlock()

# Go through each machine's directory
for machine_name in os.listdir(working_dir):
    machine_path = working_dir + os.sep + machine_name
    
    # Checking machine directory:
    if not os.path.isdir(machine_path):
        print "!! Not a directory: ", machine_path
        continue
    
    res = exp_util.find_target(machine_path, target_file)
    if res == None:
        print "!! Cannot find target file in machine dir:", machine_name
        continue
    
    # Found target file and pass it's content to processing modules
    print "Processing machine: ", machine_name
    print "-- Processing file: ", res
    
    # Go through the file to get information
    for index, line in enumerate( open( res)):
        time_proc.parse_time(line)
        finger_parser.parse(line)
        dblock_lat_parser.parse(line)

# Begin to output results; and put them into output dir:

# Output experiment times to a file in output directory:
print "-- Experiment start from", time_proc.get_times()
time_proc.save_times(output_dir)

# Output other aspects:
finger_parser.save_to_file(output_dir)
dblock_lat_parser.save_to_file(output_dir)

#for time, op_type, op_num in finger_parser:
#    print 'Time:', time, 'Type', op_type, 'Num:', op_num
