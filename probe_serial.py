"""
file: probe_serial.py
date: February 2017
description: This file contains the code for the task responsible for listening 
    to incoming serial data from the Ludlum probe.

    The data that is read in is written to a file and tagged with the current
    location data, imported from a different module.

"""


import time
import serial
from struct import *

import wiringpi
#from dual_mc33926_rpi_4raster import motor

# For if we wanna keep drivers in a separate directory - can use 'load_source'
from imp import load_source
path_to_drivers='raster_driver/'
load_source('dual_mc33926_rpi_4raster.motor', path_to_drivers) 

# Need to import a module that will be updating the current estimated location
# import localization

# Global variable to track the 'next sweep direction' of the scanner. Starts
# at 1 (run initialize_raster_scanner() to ensure this is correct and that the
# scanner is working).
nxt_raster_dir = 1

scan_fname = "scan_data.txt"

#34.4 cm so sleep for 3.44 seconds until scanner reaches opposite edge 
# of the rail. Need 1147 steps total (can adjust this later)
RASTER_STEPS = 1147
RASTER_HALF_STEPS = 2*RASTER_STEPS + 1
# Need to delay in between stepper steps to get the right speed. *TUNE THIS*
STEP_DELAY = 1500



def initialize_raster_scanner():
    """
    Depending on shutdown, the raster mechanism could be on the left or right.
    This function should be run on start-up to ensure it's always on the left,
    corresponding to the initial value of raster_side_flag=1
    """
    # NEED TO VERIFY WHICH DIRECTION FOR OUR APPARATUS CORRESPONDS TO "LEFT"
    # WILL ASSUME motor.setDirection(0) MEANS LEFT
    motor.enable()
    nxt_raster_dir = 0 # 
    motor.setDirection(nxt_raster_dir)
    state = 0
    for half_step in range(RASTER_HALF_STEPS):
        motor.toggleSquare(state)
        state = 1 - state
        wiringpi.delayMicroseconds(STEP_DELAY)
    nxt_raster_dir = 1

def do_read_sweep():
    """ 
    Ideally, this might be the main function that gets called for reading. The
    main task will decide to initiate a read sweep at some point. This function
    must then read in scans from the probe while sweeping across.

    * V0.1 OF THIS FUNCTION: open a serial probe connection, wait for data, then
    quickly sweep halfway until more data, then all the way across, store two+ readings for the sweep *

    """
    probe = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, parity=serial.PARITY_NONE, \
                                stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
    motor.enable()
    state = 0
    motor.setDirection(nxt_raster_dir)

    data = probe.read(15) # garbage read to wait until a dump cycle occurs

    for half_step in range(0.5*RASTER_HALF_STEPS):
        motor.toggleSquare(state)
        state = 1-state
        wiringpi.delayMicroseconds(STEP_DELAY)

    """ Here's the tricky part: what if for some reason going halfway across is a
    little slow? Then this next probe.read() will cause the scanner to sit in
    the middle for a whole 2 seconds. 
     ** Might be a good reason to do a dedicated serial read task anyways ** """
    data1 = probe.read(15) 

    for half_step in range(0.5*RASTER_HALF_STEPS):
        motor.toggleSquare(state)
        state = 1-state
        wiringpi.delayMicroseconds(STEP_DELAY)
    data2 = probe.read(15) 

    # Next, acquire current location from the localization module
    # location = localization.get_curr_loc()
    loc_centr = (100.0,200.0)
    loc1 = loc_centr # TODO: do simple orientation math of raster scanner later
    loc2 = loc_centr
    save_reading(data1,loc1)
    save_reading(data2,loc2)
    probe.close()        

def save_reading(data, loc):
    """
    Takes raw data dump from Ludlum, parses and converts it, and saves it in a
    data file tagged by the location.

    ** PARAMS **
      data (bytes): the raw hex data read on the serial port
      loc (tuple of floats): Location data (could be just x,y, or x,y,bearing -
        depending on what the localization module outputs)
    """
    dat = [ord(x) for x in data]
    scalarCounts = dat[4:9]
    scalarCounts.reverse()
    # Next couple lines convert the hex numbers to decimal.
    # TODO: use an established normal method for doing this conversion
    scalarCounts = reduce(lambda x,y: x+y, [ scalarCounts[i]*(255**i) for i in range(5) ])
    f = open(scan_fname, "a")
    f.write("%d,%d,%d\n" % (scalarCounts, loc[0], loc[1]))
    f.close() 
 

def probe_continuous_read():
    """ This task is set up currently to continually accept readings and append
    them to a contaminant map. 
    
    ** CURRENTLY JUST MAPS CENTROID **
    """ 
    probe = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, parity=serial.PARITY_NONE, \
                                stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
  
    most_recent_counts = 0.0
    while True:
        print "Beginning listening on ttyUSB0 ..."

        data = probe.read(15)
        data = [ord(x) for x in data]
        scalarCounts = data[4:9]
        print "Got a reading! %x" % scalarCounts

        # Next couple lines convert the hex numbers to decimal
        scalarCounts.reverse()
        scalarCounts = reduce(lambda x,y: x+y, [ scalarCounts[i]*(255**i) for i in range(5) ])
        
        # Next, acquire current location from the localization module
        # location = localization.get_curr_loc()
        location = (100.0,200.0)

        f = open("scan_data.txt", "a")
        f.write("%d,%d,%d\n" % (scalarCounts, location[0], location[1]))
        f.close() 
    probe.close()        

if __name__=="__main__":
    """
    To run the earliest iteration of this code which writes probe data to a 
    file once, executing this file will run this code block.
    """

    '''probe.open()'''
    # Serial Connection configuration
    probe = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, parity=serial.PARITY_NONE, \
                                stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
    
    print("Connected to Serial Port")
    
    data = probe.read(15)
    data = [ord(x) for x in data]
    scalarCounts = data[4:9]
    scalarCounts.reverse()
    scalarCounts = reduce(lambda x,y: x+y, [ scalarCounts[i]*(255**i) for i in range(5) ])
    
    print(scalarCounts)

    location = (100, 20)
    
    # open text file for writing.
    file = open("scan_data.txt", "a")
    # Store Probe data and Location data to a text file
    file.write("%d,%d,%d \n" % (scalarCounts, location[0], location[1]))
    
    # Something else
    print("Finished")
    
    probe.close()


