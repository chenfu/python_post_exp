#!/usr/bin/env python

'''
This is an analysing program for string pattern discovery in trace log file of
 the Chord system.

Until now, no extra python librarys required. This a common python script
 
 9-11-2013 Fu Chen
'''


import sys, getopt, os, re

import exp_util

# This is the working direcoty, and trace_log file
working_dir = None
target_file = None
output_t = False

def parse_arg(argv):
    global working_dir
    global target_file
    global output_t
	
    try:
        opts, args = getopt.getopt(argv, "hw:t:o", ["wdir=", "target="])
    except getopt.GetoptError:
        print 'analyse_trace.py -w <working_dir> -t <target>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'trace_engine.py -w <working_dir> -t <target>'
            sys.exit(2)
        elif opt == '-w':
            working_dir = os.path.dirname(arg)
        elif opt == '-t':
            target_file = arg
        elif opt == '-o':
            output_t = True

# Getting arguments and check arguments
if __name__ == "__main__":
    parse_arg(sys.argv[1:])
    if working_dir == None:
        print '!! Please provide working directory'
        sys.exit(2)
    elif target_file == None:
        print '!! Please provide target file'
        sys.exit(2)
    
    if not os.path.isdir(working_dir):
        print '!! Working directory:', working_dir, 'does not exist'
        sys.exit(2)

# Find start time and end time
time_proc = exp_util.exp_time()

'''
In patterns list, all possible log entries are listed.
'''

patterns = ['^\d+\.\d+ lsd: starting: .+', #Starting point 
            '^\d+\.\d+ lsd: starting amain.', #Vnode starting
            '^\d+\.\d+ lsd: DHash \d+ is ready.', #DHash ready
            '^\d+\.\d+ lsd: stopping.', #Stopping point
            
            '^\d+\.\d+ dhash: [0-9A-Fa-f]+ registered dhash_program_1', #DHash starting
            
            '^\d+\.\d+ loctable: insert [0-9A-Fa-f]+,\d+\.\d+\.\d+\.\d+,\d+,\d+', #locationtable insertion
            
            # 2013-07-14-21_30_00_TO_2013-07-15-08_30_00 (uf012.cs.man.ac.uk) Very rare:
            '^\d+\.\d+ location:  set_alive yo me not dead [0-9A-Fa-f]+', # The last word is short-ID
            
            '^\d+\.\d+ finger_table: [0-9A-Fa-f]+: stabilize_finger: findsucc of finger \d+', #Fingertable insert [X]
            '^\d+\.\d+ finger_table: [0-9A-Fa-f]+: stabilize_finger_getpred_cb: fixing finger \d+', #Fingertable fix [X]
            
            '^\d+\.\d+ dhblock_chash: db write: [0-9A-Fa-f]+ N [0-9A-Fa-f]+ \d+ [0-9A-Fa-f]+', #Berkeley DB writing
            
            '^\d+\.\d+ dhash_store: [0-9A-Fa-f]+: dhash_store::store \([0-9A-Fa-f]+:\d+, \d+, \d+, \d+, \d+\)', #DHash Fragment store
            '^\d+\.\d+ dhash_store: [0-9A-Fa-f]+: dhash_store::finish \([0-9A-Fa-f]+:\d+, \d+, ..., \d+, RPC: Success\)', #DHash Fragment ack
            '^\d+\.\d+ dhash_store: [0-9A-Fa-f]+: dhash_store::done \([0-9A-Fa-f]+:\d+\)', #DHash Fragment done
            '^\d+\.\d+ dhash_store: [0-9A-Fa-f]+: dhash_store::finish \([0-9A-Fa-f]+:\d+, \d+, ..., \d+, RPC: Unable to receive\)', #DHash Frag recv fail ack
            '^\d+\.\d+ dhash_store: store failed: [0-9A-Fa-f]+:\d+: RPC error RPC: Unable to receive', #DHash Frag recv fail done
            '^\d+\.\d+ dhash_store: [0-9A-Fa-f]+: dhash_store::finish \([0-9A-Fa-f]+:\d+, \d+, ..., \d+, RPC: Unable to send\)', #DHash Fragment send fail ack
            '^\d+\.\d+ dhash_store: store failed: [0-9A-Fa-f]+:\d+: RPC error RPC: Unable to send', #DHash Frag send fail done
            '^\d+\.\d+ dhash_store: [0-9A-Fa-f]+: dhash_store::finish \([0-9A-Fa-f]+:\d+, \d+, ..., \d+, RPC: Timed out\)', #DHash Frag timeout ack
            '^\d+\.\d+ dhash_store: store failed: [0-9A-Fa-f]+:\d+: RPC error RPC: Timed out', #DHash Frag timeout done
            
            #<CAUTION>: In the later experiments, each block has only one fragment.
            '^\d+\.\d+ dhashcli: store [0-9A-Fa-f]+ \(frag \d+/\d+\) -> [0-9A-Fa-f]+ in \d+ms: [DHASH_OK|DHASH_TIMEOUT]', #DHash Block store [X]
            '^\d+\.\d+ dhashcli: [0-9A-Fa-f]+: store \([0-9A-Fa-f]+\): only stored \d+ of \d+ encoded.', #DHash Block timeout [X]
            '^\d+\.\d+ dhashcli: [0-9A-Fa-f]+: store \([0-9A-Fa-f]+\): failed; insufficient frags/blocks stored.', #DHash Block failure [X]
            # fetch part:
            '^\d+\.\d+ dhashcli: [0-9A-Fa-f]+: dhashcli::sendblock \([0-9A-Fa-f]+:\d\) to dest: [0-9A-Fa-f]+,[0-9\.]+,\d+,\d+', # dhash/client.C
            '^\d+\.\d+ dhashcli: [0-9A-Fa-f]+: dhashcli::sendblock \([0-9A-Fa-f]+:\d\) adbd request sent', # together with above for block fetch
            '^\d+\.\d+ dhashcli: [0-9A-Fa-f]+: dhashcli::sendblock_fetch_cb \([0-9A-Fa-f]+:\d\) has been fetched [0-9A-Fa-f]+,[0-9\.]+,\d+,\d+, stat [ADB_OK|ADB_ERR|ADB_NOTFOUND|ADB_COMPLETE|ADB_DISKFULL]', # comeback block fetch, 
            
            '^\d+\.\d+ dhashcli: [0-9A-Fa-f]+: retrieve \([0-9A-Fa-f]+:\d\): new retrieve', # dhash/client.C 128 blockID is in dhash/dhash_common.h 
            '^\d+\.\d+ dhashcli: [0-9A-Fa-f]+: retrieve_verbose \([0-9A-Fa-f]+:\d\): route [0-9A-Fa-f ]+',
            '^\d+\.\d+ dhashcli: [0-9A-Fa-f]+: retrieve_verbose \([0-9A-Fa-f]+:\d\): succs [0-9A-Fa-f ]+', #dhash/client.C 188 retrieval lookup results
            '^\d+\.\d+ dhashcli: [0-9A-Fa-f]+: retrieve \([0-9A-Fa-f]+:\d\): failed from successor [0-9A-Fa-f]+,[0-9\.]+,\d+,\d+',
            '^\d+\.\d+ dhashcli: [0-9A-Fa-f]+: retrieve \([0-9A-Fa-f]+:\d\): out of successors; failing.',
            '^\d+\.\d+ dhashcli: [0-9A-Fa-f]+: retrieve_verbose \([0-9A-Fa-f]+:\d\): read from [0-9A-Fa-f]+',
            '^\d+\.\d+ dhashcli: [0-9A-Fa-f]+: retrieve \([0-9A-Fa-f]+:\d\): timeout \d+ on [0-9A-Fa-f]+,[0-9\.]+,\d+,\d+', #dhash/client.C 278 retry_num after 'timeout'
            '^\d+\.\d+ dhashcli: [0-9A-Fa-f]+: retrieve \([0-9A-Fa-f]+:\d\): unexpected fragment from [0-9A-Fa-f]+,[0-9\.]+,\d+,\d+, discarding.',
            
            # Dhash block error (Quite Rare): 06_23_2011 (gfpc125.cs.man.ac.uk)
            '^\d+\.\d+ dhblock_chash: retrieve \([0-9A-Fa-f]+:\d\): verify failed.',
            '^\d+\.\d+ dhashcli: [0-9A-Fa-f]+: retrieve_verbose \([0-9A-Fa-f]+:\d\): err',
            '^\d+\.\d+ dhblock_chash: retrieve \([0-9A-Fa-f]+:\d\): duplicate fragment retrieved from successor; same as fragment \d+',
            
            #Other
            '^\d+\.\d+ vnode: COORD: ignored actual of \d+.\d+', #chord/server.C 782
            
            '^\d+\.\d+ vnode: [0-9A-Fa-f]+: find_succlist \([0-9A-Fa-f]+\): skipping \d+ nodes.', #chord/server.C 188
            ]

start_from = 'uf012.cs.man.ac.uk'
skip = False

# Go through each machine's directory
for machine_name in os.listdir(working_dir):
    if machine_name == start_from:
        skip = False
    
    if skip:
        continue
    
    machine_path = working_dir + os.sep + machine_name
    
    # Checking machine directory:
    if not os.path.isdir(machine_path):
        #print "!! Not a directory: ", machine_path
        continue
    
    res = exp_util.find_target(machine_path, target_file)
    #print "*** res = ", res
    if res == None:
        print "!! Cannot find target file in machine dir:", machine_name
        continue
    
    # Found target file and pass it's content to processing modules
    print "Processing machine: ", machine_name
    print "-- Processing file: ", res
    
    # Go through a single file to check unknown information.
    for index, line in enumerate( open( res)):
        time_proc.parse_time(line)
            
        line_num = index + 1
        found = False
        
        for pat_string in patterns:
            pat = re.compile(pat_string)
            m = pat.match(line)
            
            if m:
                found = True
                break
        
        if not found:
            print "<", line_num, ">: ", line
            sys.exit(2)

    print "Complete machine: ", machine_name

def check_dir(check_dir, target):
    target_file = check_dir + os.sep + target
    if os.path.isdir(target_file):
        print 'Has \'', target, '\' directory'
    else:
        print 'NO  \'', target, '\' directory'

def check_file(check_dir, target):
    target_file = check_dir + os.sep + target
    if os.path.isfile(target_file):
        print 'Has \'', target, '\' file'
    else:
        print 'NO  \'', target, '\' file'

#check_dir(working_dir, 'report')
#report_dir = working_dir + os.sep + 'report'
#check_dir(report_dir, 'settings')

check_dir(working_dir, '_plot')
check_dir(working_dir, '_procd_result')
proc_dir = working_dir + os.sep + '_procd_result'
check_file(proc_dir, 'setting')

if output_t:
    (start_t, end_t) = time_proc.get_times()
    
    print "Working directory:", working_dir
    print "-- Experiment start from", start_t, "to", end_t
    time_file = working_dir + os.sep + 'time'
    with open(time_file, 'w') as time_p:
        time_p.writelines([str(start_t), '\n', str(end_t)])
