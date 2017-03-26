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

#wiringpi.wiringPiSetupGpio()
# Temporarily: global flag indicating a scan sweep is in progress
scanning=False
direction = 1
rast_dir = 1
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
    global direction
    global rast_dir
    
    # TODO: implement a 'final check' when we've reached bottom right 
    turn_counter = 0

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
            #For now, let us use forward increments of 12.5cm
            move.move_here(locat,(locat['x'],locat['y']+12.5*direction))
            print(locat)
        else:
            turn_counter += 1
            if turn_counter >= 6:
                print("Reached 6 walls!")
                break
            turn_routine()
    return

def test_position_tags():
    """
    Endlessly scan and move forward 3 times before scanning and turning around.
    Tests position tag fidelity and whether turns fuck things up. Uses a new
    localization function to just save the centroid.
    """
    import RPi.GPIO as GPIO
    GPIO.setup(7, GPIO.OUT)
    GPIO.output(7,0)
    GPIO.setup(7, GPIO.IN)

    probe.initialize_raster_scanner()
    global direction
    global rast_dir
    scan_counter = 0
    while True:
        scan_counter += 1
        scanning=True
        probe.do_read_sweep(locat, rast_dir)
        scanning=False
        rast_dir = -rast_dir + 1
    
        # move_one_increment()
        if scan_counter >= 3:
            turn_routine()
            scan_counter = 0
            direction = -1*direction
        else:
            move.move_here(locat,(locat['x'],locat['y']+12.5*direction))
            localization.save_position(locat)
        if GPIO.input(7)==1:
            print("Finishing position tag test")
            break
    return


def turn_scan(up_or_down):
    global rast_dir
    i = 0
    dx = 10.0
    if up_or_down:
        dPhi = -15.0
    else:
        dPhi = 15.0
    while i<1:
        i += 1
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
            #For now, let us use forward increments of 12.5cm
            move.move_here(locat,(locat['x']+dx,locat['y']))
            print(locat)
        else:
           break

    scanning=True
    probe.do_read_sweep(locat, rast_dir)
    scanning=False
    rast_dir = -rast_dir + 1
    while i < 4:
        i += 1
        reading, wall_found = read_IR(0,0)
        print(wall_found)

        if not wall_found:
            print('About to pivot')
            move.pivot(locat,dPhi)
            scanning = True
            probe.do_read_sweep(locat, rast_dir)
            scanning = False
            rast_dir = -rast_dir + 1
            print(locat)
    return

def turn_routine():
    '''This is currently a naive turning routine. Once the robot has detected
        a wall and stopped, This function can be called to turn it around.
        First the robot will back up so it has space to turn, turn 90 degrees
        scan a bit, and turn 90 degrees again. The final position should be one
        robot width to the side, and facing away from the detected wall'''
    global direction
    move.back_up(locat)
    
    if (0 <= locat['phi'] and locat['phi'] < 90) or (270 <= locat['phi'] and locat['phi'] <= 360):
    
        move.look_here(locat,90)
        turn_scan(False)
        move.look_here(locat,180)

    else:

        move.look_here(locat,90)
        turn_scan(True)
        move.look_here(locat,0)
        
    direction = -direction
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
    
