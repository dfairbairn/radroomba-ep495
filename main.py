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
import movement_package as move
import wiringpi
#from __future__ import print_function
from dual_mc33926_rpi_4raster import motor
from dual_mc33926_rpi import motors, MAX_SPEED
from Adafruit_BNO055 import BNO055
from localization import *
from IR_ADC_reader import read_IR
from struct import *
wiringpi.wiringPiSetupGpio()
def straight_line_test():
    """
    Basic straight-line test loop
    """
    # e.g: thread.start_new_thread( <func_name>, (args))
  # thread.start_new_thread( wall_detector_thread, ("Wall Detector task",0.25) )
    # Initialize the raster scanner
    probe_serial.initialize_raster_scanner()
    rast_dir = 1
    # Create location data for the run
    locat = locat_create()
    #Initialize the IMU
    IMU_initialize()
    while True:
        # Read front sensor (0) don't bother tracking last_read measurement (0)
        reading, wall_found = read_IR(0,0)
        print(wall_found)

        if not wall_found:
            # do_read_sweep()
            probe_serial.do_read_sweep(locat, rast_dir)
            rast_dir = -rast_dir + 1
            reading, wall_found = read_IR(0,0)
            # move_one_increment()
        if not wall_found:
            #For now, let us use forward increments of 14.5cm
            move.move_here(locat,(locat['x'],locat['y']+14.5))
            print(locat)
        else:
            break
    return

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
    print(threadName," has started up!")
    time.sleep(delayTime)
    print(threadName," is exitting.")
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

if __name__ == '__main__':
    straight_line_test()
    
