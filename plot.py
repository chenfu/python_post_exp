#!/usr/bin/env python

'''
This script is used to produce plots from collected and aggregated experiment
 result.

Input: a directory with processed experiment results 
        (a 'time' file is necessary in this directory)
    
Output: The plot of each result file in input directory except for the 'time'


Fu Chen 19/06/2013

'''

import sys, os, getopt, re

from pandas import Series, DataFrame
import pandas as pd

#from datetime import datetime
#from functools import partial

import matplotlib.pyplot as plt

import exp_util

working_dir = None
output_dir = None
resolution = '5S' #default sampling resolution is 5 seconds

output_fmt = '.pdf' #default output format is PDF

setting_file = None

def parse_arg(argv):
    global working_dir
    global output_dir
    global resolution
    global output_fmt
    global setting_file

    try:
        opts, args = getopt.getopt(argv, "hw:r:f:o:s:", ["wdir=", "res=", "format=", "odir=", "setting="])
    except getopt.GetoptError:
        print 'plot.py -w <working_dir> -r <resolution> -f <output_format> -o <output_dir> -s <setting_file>'
	sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'plot.py -w <working_dir> -r <resolution> -f <output_format> -o <output_dir> -s <setting_file>'
            sys.exit(2)
        elif opt == '-w':
            working_dir = os.path.dirname(arg)
        elif opt == '-r':
            resolution = arg
        elif opt == '-f':
            output_fmt = arg
        elif opt == '-o':
            output_dir = arg
        elif opt == '-s':
            setting_file = arg

if __name__ == "__main__":
    parse_arg(sys.argv[1:])
    if working_dir == None:
        print '!! Please provide working directory'
        sys.exit(2)
    elif output_dir == None:
        print '!! Please provide output directory name'
        sys.exit(2)
    
    if not os.path.isfile(setting_file):
        print '!! Need a setting file provided'
        sys.exit(2)
    
    if not os.path.isdir(working_dir):
        print '!! Working directory:', working_dir, 'does not exist'
        sys.exit(2)
    
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


# Load experiment start time and end time
# Assign exp's start time and end time
start_time = None
end_time = None

time_file = working_dir + os.sep + 'time'
if not os.path.isfile(time_file):
    print 'Working dir has no time file:', working_dir
    sys.exit(2)
time_strs = [x.rstrip() for x in open(time_file)]

time_dict = {int(time_strs[0]):0, int(time_strs[1]):0}
time_index = Series(time_dict)
time_index.index = time_index.index.astype('datetime64[s]')
time_index.index = time_index.index.tz_localize('UTC')
time_index.index = time_index.index.tz_convert('Europe/London')

start_time = time_index.index[0]
end_time = time_index.index[1]

# Load experiment stages from setting file
time_bound = exp_util.get_stages(setting_file)

# Plot a dataFrame:
def plot_data(data_set, save_filename):
    fig = plt.figure()
    
    ax1 = fig.add_axes([0.1, 0.4, 0.5, 0.5])
    
    #data_set.plot(ax = ax1, style = 'rs')
    data_set.plot(ax = ax1, marker = 'o', ls = '*', color = 'red')
    #data.plot(ax = ax1, style = 'rs', xlim = (start_time, end_time))
    #data.plot(ax = ax1, kind='bar')
    
    output_plot = output_dir + os.sep + os.path.basename(save_filename) + output_fmt
    fig.savefig(output_plot)

def plot_val_data(data_set, save_filename):
    fig = plt.figure()
    
    ax1 = fig.add_axes([0.1, 0.4, 0.5, 0.5])
    
    #data_set.plot(ax = ax1, style = 'rs')
    data_set.plot(ax = ax1)
    #data.plot(ax = ax1, style = 'rs', xlim = (start_time, end_time))
    #data.plot(ax = ax1, kind='bar')
    
    output_plot = output_dir + os.sep + os.path.basename(save_filename) + output_fmt
    fig.savefig(output_plot)

# Processing a source file, 'file_name' is a absolute path to a source file
def process_file(file_name):
    data = pd.read_table(file_name, index_col='Time')# Load data
    data.index = data.index.astype('datetime64[s]')# Convert to data index
    data.index = data.index.tz_localize('UTC')
    data.index = data.index.tz_convert('Europe/London')
    
    # Reindex data to a second resolution with 0 as fill_value
    data = data.reindex(pd.date_range(start=start_time, end=end_time, freq='s'), fill_value=0)
    
    # Resample according to different given resolution
    data = data.resample(resolution, how='sum', closed='left', label='left')
    
    plot_data(data, os.path.basename(file_name)) # Whole exp

# Each single experiment stage is separated from the whole experiment duration.
def process_file_singel(file_name):
    data = pd.read_table(file_name, index_col='Time')# Load data
    data.index = data.index.astype('datetime64[s]')# Convert to data index
    data.index = data.index.tz_localize('UTC')
    data.index = data.index.tz_convert('Europe/London')
    
    # Reindex data to a second resolution with 0 as fill_value
    data = data.reindex(pd.date_range(start=start_time, end=end_time, freq='s'), fill_value=0) 
    
    # Get and process each experiment stage's data then put them together to return
    for time_s, time_e in time_bound:
        print 'Time from:', time_s, 'to:', time_e
        tmp_data = data[time_s:time_e].copy()
 
        tmp_data = tmp_data.resample(resolution, how='sum', closed='left', label='left')
        
        print tmp_data

# Processing value based experiemnt parametres: 
def process_val_file(file_name):
    data = pd.read_table(file_name, index_col='Time')# Load data
    data.index = data.index.astype('datetime64[s]')# Convert to data index
    data.index = data.index.tz_localize('UTC')
    data.index = data.index.tz_convert('Europe/London')
    
    # Reindex data to a second resolution with 0 as fill_value
    data = data.reindex(pd.date_range(start=start_time, end=end_time, freq='s'), fill_value=0) 
    
    # Get and process each experiment stage's data then put them together to return
    for time_s, time_e in time_bound:
        print 'Time from:', time_s, 'to:', time_e
        tmp_data = data[time_s:time_e].copy()
 
        tmp_data = tmp_data.resample(resolution, how='sum', closed='left', label='left')
        
        print tmp_data
    
    # use all_data to replace the original data, for further resolution adjustion
    # the current resolution is 1 second
    #all_index = pd.date_range(start=start_time, end=end_time, freq='s')
    #ser_data = Series(0, index=all_index)
    #ser_data.name = data.columns[0]
    #ser_data.index.name = data.index.name
    #
    #all_data = DataFrame(ser_data)
    #
    #all_data = all_data.add(data, fill_value=0)
    #all_data = all_data[data.columns[-1]]
    
        #all_data = all_data.add(data)
    
    #all_data = all_data.resample(resolution, how='mean', closed='left', label='left')
    
    # TODO: There should be a resampling here for different resolution:
    
    #plot_val_data(all_data, os.path.basename(file_name)) # Whole exp

# Test
test_file = working_dir + os.sep + 'Finger_Fix'
#process_file(test_file)

#test_file = working_dir + os.sep + 'DHash_Succ_Store_VAL'
process_val_file(test_file)

'''
# Plotting Configuration
font_options = {'family' : 'monospace',
                'weight' : 'normal',
                'size'   : 16}
plt.rc('font', **font_options)

operation_list = {'file_insert': ('Insertion', 'insert'),
                  'file_fetch': ('Fetching', 'fetch')}

# This function plot the instruction for the given operation, 
#   which comes from the setting file.
# TODO: make correlation later.
def plot_inst(op):
    pat = re.compile('^TIMES:(\d+).\d+-(\d+).\d+')
    pat2 = re.compile('(\d+):(\d+);')
    
    filename = working_dir + '/_procd_result/setting'
    inst_dict = {}
    start_time = 0
    end_time = 0
    for line in open(filename, 'r'):
        line = line.rstrip()
        m = pat.match(line)
        if m:
            start_time = int(m.group(1))
            end_time = int(m.group(2))
            
        if line.find(op + '_instruction') != -1:
            inst = line[line.find(':') + 1:]
            if inst == '0':
                return (-1, -1)
            for time, interval in pat2.findall(inst):
                inst_dict[int(time)] = float(interval)
            last_time = line[line.rfind(';') + 1:]
            inst_dict[int(last_time)] = float('NaN')
    
    # Add start time and end time
    inst_dict[0] = float('NaN')
    inst_dict[end_time - start_time] = float('NaN')
    
    inst_s = Series(inst_dict)
    inst_s.index = inst_s.index + start_time
    inst_s.index = inst_s.index.astype('datetime64[s]')
    inst_s.index = inst_s.index.tz_localize('UTC')
    inst_s.index = inst_s.index.tz_convert('Europe/London')
    
    inst_s = inst_s.apply(lambda x: 0.0 if x == 0 else (x ** -1) * 60 )
    inst_s = inst_s.fillna(0)
    
    inst_s = inst_s.resample('5S', fill_method = 'ffill')
    
    if op == 'insert':
        title_str = 'Insert'
    else:
        title_str = 'Fetch'
    
    # Setting up ploting
    plt.rc('figure', figsize=(20, 15))
    plt.figure()
    
    plt.title(title_str + ' Operation Instruction')
    plt.xlabel('Time')
    plt.ylabel('Number of ' + title_str + ' per Minute')
    
    inst_s.plot(legend = True, label = title_str + ' rate')
    
    output_file = output_dir + '/' + op + '_inst' + format
    plt.savefig(output_file)
    
    return (inst_s.index[0], inst_s.index[-1])


# Plot list which have Title, y_label, and legend:
plot_list = {'block_num': ('Number of Blocks ', 'Block number', 'Block number'),
             'succ_rate': ('Successful Rate of Block ', 'Success Rate (%)', 'Success rate'),
             'latency': ('Average latency of Block ', 'Latency (nanosecond/byte)', 'Average Latency'),
             'hops': ('Average hops of Block ', 'Hops', 'Average Hops'),
             'queue_time': ('Average waiting time of Block ', 'Waiting time ns (nanosecond)', 'Waiting time'),
}

# This function plots all block operations
def plot_all(data, target, opt, start_t, end_t):
    #plot settings
    plt.rc('figure', figsize=(20, 15))
    
    fig = plt.figure()
    
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.set_title(plot_list[target][0] + operation_list[opt][0])
    ax1.set_ylabel(plot_list[target][1])

    data.plot(ax = ax1, legend = True, label = plot_list[target][2], xlim = (start_t, end_t), ylim = (data.min()*0.9, data.max()*1.1))
    
    output_file = output_dir + '/'+ target+ '_all' + format
    plt.savefig(output_file)

# This function plots each type block separately
def plot_type(inode_data, indirect_data, data_data, target, opt, start_t, end_t):
    plt.rc('figure', figsize=(15, 20))
    plt.xlim((start_t, end_t))
    fig = plt.figure()
    
    # Set three sub plots.
    ax1 = fig.add_subplot(3, 1, 1)
    ax1.set_title(plot_list[target][0] + '(inode Blocks) ' + operation_list[opt][0])
    ax1.set_ylabel(plot_list[target][1])

    ax2 = fig.add_subplot(3, 1, 2)
    ax2.set_title(plot_list[target][0] + '(indirect Blocks) ' + operation_list[opt][0])
    ax2.set_ylabel(plot_list[target][1])
    
    ax3 = fig.add_subplot(3, 1, 3)
    ax3.set_title(plot_list[target][0] + '(data Blocks) ' + operation_list[opt][0])
    ax3.set_ylabel(plot_list[target][1])
    
    y_inode_up = inode_data.max() * 1.1
    y_inode_down = inode_data.min() * 0.9
    
    y_indirect_up = indirect_data.max() * 1.1
    y_indirect_down = indirect_data.min() * 0.9
    
    y_data_up = data_data.max() * 1.1
    y_data_down = data_data.min() * 0.9
        
    inode_data.plot(ax = ax1, legend = True, label = plot_list[target][2] + '(inode Blocks) ', xlim = (start_t, end_t), ylim = (y_inode_down, y_inode_up))
    indirect_data.plot(ax = ax2, legend = True, label = plot_list[target][2] + '(indirect Blocks) ', xlim = (start_t, end_t), ylim = (y_indirect_down, y_indirect_up))
    data_data.plot(ax = ax3, legend = True, label = plot_list[target][2] + '(data Blocks) ', xlim = (start_t, end_t), ylim = (y_data_down, y_data_up))
    
    output_file = output_dir + '/' + target + '_types' + format
    plt.savefig(output_file)

# This function produce Series according to the sum of duplicated data
def proc_sum(column, data):
    proc_d =  data[column].resample(str(resolution) + 's', how = 'sum', closed = 'right', label = 'right')
    _ = proc_d.fillna(0, inplace = True)
    return proc_d

# This function produce Series according to the average of duplicated data
def proc_ave(column, data):
    proc_d =  data[column].resample(str(resolution) + 's', how = 'mean', closed = 'right', label = 'right')
    proc_d = proc_d.dropna()
    return proc_d

# Calculate the hop specifically.
def proc_hop(data):
    proc_d = data[data.succ == 1]['hop']
    proc_d = proc_d.resample(str(resolution) + 's', how = 'mean', closed = 'right', label = 'right')
    proc_d = proc_d.dropna()
    return proc_d

# Calculate the latency for every byte
def proc_lat(data):
    proc_data = data[['size', 'latency']]
    proc_data = proc_data.apply(lambda x: float(x['latency']) / float(x['size']), axis = 1)
    proc_data = proc_data.resample(str(resolution) + 's', how = 'mean', closed = 'right', label = 'right')
    _ = proc_data.fillna(0, inplace = True)
    
    return proc_data
    
# Calculate the success rate specifically
#  drop the time point where both succ and fail are absent. fill na with zero.
def proc_rate(data):
    proc_data = data[['succ', 'fail']].resample(str(resolution) + 's', how = 'sum', closed = 'right', label = 'right')
    proc_data = proc_data.dropna(how = 'all')
    _ = proc_data.fillna(0, inplace = True)
    proc_data = proc_data.apply(lambda x: float(x['succ'] * 100) / float(x['succ'] + x['fail']), axis = 1)
    
    return proc_data
    
# XXX This list includes target name, and its process functions and then its index column.
target_list = {
               'block_num': (partial(proc_sum, 'count'), 'Start_Time'),
               'queue_time': (partial(proc_ave, 'queue_time'), 'Start_Time'),
               'succ_rate': (proc_rate, 'Sent_Time'),
               'latency' : (proc_lat, 'Sent_Time'),
               'hops' : (proc_hop, 'Sent_Time'),
}

def load_data(filename):
    # Read in data.
    data_file = working_dir + '/_procd_result/' + filename
    
    data = pd.read_csv(data_file)
    
    for key_o in operation_list.keys():
        print key_o
        (start, end) = plot_inst(operation_list[key_o][1])
        if start == -1 or end == -1:
            continue
        print start, end
        
        for key, value in target_list.iteritems():
            if data.index.name != value[1]:
                data.reset_index(inplace = True)
                data.set_index(value[1], inplace = True)
                if not isinstance (data.index, DatetimeIndex):
                    data.index = data.index.astype('datetime64[s]')
                    data.index = data.index.tz_localize('UTC')
                    data.index = data.index.tz_convert('Europe/London')
            
            data = data[data.operation == key_o]
            if len(data) == 0:
                continue
                
            if machine != None:
                data = data[data.Machine == machine]
            
            print key
            proc_data_all = value[0](data)
        
            proc_data_inode = value[0](data[data.type == 'inode'])
            proc_data_indirect = value[0](data[data.type == 'indirect'])
            proc_data_data = value[0](data[data.type == 'data'])
        
            plot_all(proc_data_all, key, key_o, start, end)
            plot_type(proc_data_inode, proc_data_indirect, proc_data_data, key, key_o, start, end)


if __name__ == "__main__":
     
    if not os.path.isdir(working_dir + '/_procd_result'):
        print "Unknown experiment result directory:", working_dir + '/_procd_result'
        sys.exit(2)
    
    if machine != None:
        # Prepare output dir:
        output_dir += '/' + machine
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
    
    load_data('block_ALL')
'''