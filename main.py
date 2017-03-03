#!/usr/bin/python
"""
file: 'main.py'
date: February 2017

description: 
    Possibly our main python script containing the master task for the robot?

    For now I just have the script portion of this file calling a specific 
    function for the main loop.

"""
import thread 
# use this like: thread.start_new_thread( <func_name>, (args) ) where args
# are the args intended to be provided to func_name.  
import time
import probe_serial

from IR_ADC_reader import read_IR

def straight_line_test():
    """
    Basic straight-line test loop
    """
    # e.g: thread.start_new_thread( <func_name>, (args))
    thread.start_new_thread( wall_detector_thread, ("Wall Detector task",0.25) )
    while True:
        # Read front sensor (0) don't bother tracking last_read measurement (0)
        reading, wall_found = read_IR(0,0)
        if not wall_found:
            # do_read_sweep()
            # move_one_increment()

def wall_detector_thread(threadName, delayTime=0.25):
    """ Loops, checking for front IR sensors indicating wall proximity. """
    print('Inter-IR sensor reads performed at intervals of: ' + str(delayTime)) 
    last_read = 0
    while True:
        result = read_IR(0, last_read) # get result for channel 0
        last_read = result[0] # Store new last_read
        if result[1]: # check the wall
            print("Wall found!")
            break
        time.sleep(delayTime) # wait for a bit

    # Do interruption stuff 

           

def dummy_serial_task(threadName, delayTime):
    """ Placeholder for probe handler task. Could just call probe code."""
    print threadName," has started up!"
    time.sleep(delayTime)
    print threadName," is exitting."
    return None

def dummy_sensor_task(threadName, delayTime):
    """ Placeholder for sensor polling task. """
    print threadName," has started up!"
    time.sleep(delayTime)
    print threadName," is exitting."
    return None

def simple_main_task():
    """
    First thread runs this function and will spawn child tasks accordingly.
    
    """
    # Start serial probe thread and task ...
    # e.g: thread.start_new_thread( <func_name>, (args))
    thread.start_new_thread( dummy_serial_task, ("Probe-task",2) )
    # Start thread for polling sensors if deemed necessary...
    # e.g. thread.start_new_thread( <
    thread.start_new_thread( dummy_sensor_task, ("Sensor-task",4) )

    # e.g. initialize operational mode-related variables?
    while True:
        # Check current state of sensors
        # wall_found = check_IR() ... 

        # Decide what to do next based on sensor state and op-mode state?
        # if not wall_found:
        #   move_one_increment()
        #   do_read_sweep()

        time.sleep(0.5)  # Placeholder code
        print "Another sleepy iteration of the main loop!"



#==============================================================================
#  Script portion
#==============================================================================

simple_()
