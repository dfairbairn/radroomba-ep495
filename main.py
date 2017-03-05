#!/usr/bin/python
"""
file: 'main.py'
date: February 2017

description: 
    Contains the main command and decision-making program for CURIE.
    
    straight_line_test() performs a naive test of robot functionality.

    main() will contain the full (basic) command code

"""
import thread 
# use this like: thread.start_new_thread( <func_name>, (args) ) where args
# are the args intended to be provided to func_name.  
import time
import probe_serial as probe
import movement_package as move
import wiringpi
#from __future__ import print_function
from hwdrivers.dual_mc33926_rpi_4raster import motor
from hwdrivers.dual_mc33926_rpi import motors, MAX_SPEED
#from Adafruit_BNO055 import BNO055
from localization import *
from IR_ADC_reader import read_IR
from struct import *

wiringpi.wiringPiSetupGpio()

# Temporarily: global flag indicating a scan sweep is in progress
scanning=False

# Create location data for the run
locat = locat_create()
# Initialize the IMU
IMU_initialize()


def straight_line_test():
    """
    Basic straight-line test loop
    """
    # e.g: thread.start_new_thread( <func_name>, (args))
    #thread.start_new_thread( wall_detector_thread, ("Wall Detector task",0.25) )
    # Initialize the raster scanner
    probe.initialize_raster_scanner()
    rast_dir = 1
    while True:
        # Read front sensor (0) don't bother tracking last_read measurement (0)
        reading, wall_found = read_IR(0,0)
        print(wall_found)

        if not wall_found:
            # do_read_sweep()
            scanning=True
            probe.do_read_sweep(locat, rast_dir)
            scanning=False
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
        if result[1] and False==scanning: # check the wall
            print("Detector thread says wall found!")
            break
        time.sleep(delayTime) # wait for a bit

    # Do interruption stuff 
    stop_everything()

def stop_everything():
    """ 
    Once the robot has completed its mission this function can stop all things.
    """
    import sys
    motor.disable()
    motors.disable() 
    sys.exit()

#==============================================================================
#  Script portion
#==============================================================================

if __name__ == '__main__':
    straight_line_test()
    
