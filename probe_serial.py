"""
file: probe_serial.py 
description: This file contains the code for the task responsible for listening 
    to incoming serial data from the Ludlum probe.

    The data that is read in is written to a file and tagged with the current
    location data, imported from a different module.
date: February 2017

"""


import time
import serial
import localization
import math
from struct import *

import wiringpi
from hwdrivers.dual_mc33926_rpi_4raster import motor
# In future:
# from hwdrivers.raster import motor

# Need to import a module that will be updating the current estimated location
# import localization

# Global variable to track the 'next sweep direction' of the scanner. Starts
# at 1 (run initialize_raster_scanner() to ensure this is correct and that the
# scanner is working).
nxt_raster_dir = 0 

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
    state = 0
    motor.enable()
    nxt_raster_dir = 0 # 
    motor.setDirection(nxt_raster_dir)
    for half_step in range(RASTER_HALF_STEPS):
        motor.toggleSquare(state)
        state = 1-state
        wiringpi.delayMicroseconds(STEP_DELAY//2)
    nxt_raster_dir = 1
    motor.disable()
    return

def do_read_sweep(locat, nxt_dir=0):
    """ 
    Ideally, this might be the main function that gets called for reading. The
    main task will decide to initiate a read sweep at some point. This function
    must then read in scans from the probe while sweeping across.

    * V0.1 OF THIS FUNCTION: open a serial probe connection, wait for data, then
    quickly sweep halfway until more data, then all the way across, store two+ readings for the sweep *
    
    Currently takes nxt_dir as an argument optionally
    TODO: integrate a global nxt_raster_dir variable
    """
    probe = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, parity=serial.PARITY_NONE, \
                                stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout = 3)

    try:
        data = extract_counts(probe.read(15)) # garbage read to wait until a dump cycle occurs
    except:
        data = extract_counts('0 0 0 0 0 0 0 0 0 0 0 0 0 0 0')
        
    state=0
    motor.enable()
    motor.setDirection(nxt_dir)
    
    for half_step in range(int(0.5*RASTER_HALF_STEPS)):
        motor.toggleSquare(state)
        state = 1-state
        wiringpi.delayMicroseconds(STEP_DELAY)

    """ Here's the tricky part: what if for some reason going halfway across is a
    little slow? Then this next probe.read() will cause the scanner to sit in
    the middle for a whole 2 seconds. 
     ** Might be a good reason to do a dedicated serial read task anyways ** """

    motor.disable()
    try:
        data1 = extract_counts(probe.read(15)) - data
    except:
        data1 = extract_counts('0 0 0 0 0 0 0 0 0 0 0 0 0 0 0')
    motor.enable()

    for half_step in range(int(0.5*RASTER_HALF_STEPS)):
        motor.toggleSquare(state)
        state = 1-state
        wiringpi.delayMicroseconds(STEP_DELAY)
    motor.disable()
    try:
        data2 = extract_counts(probe.read(15)) - data1 - data #Changed to minus data1 - Dan March 5
    except:
        data2 = extract_counts('0 0 0 0 0 0 0 0 0 0 0 0 0 0 0')
        
    #counts = dat[4:9]
    # Next, acquire current location from the localization module
    #locat = localization.locat_create()
    x, y, phi = localization.get_position(locat)
    loc_centr = (x,y,phi) # robot center
    phirad = phi*3.1415926535/180
    # The scanner axis seems to roughly be 12 cm ahead of robot centroid and
    # from center (front IR probe), center of probe at leftmost/rightmost seems
    # to be +/- 17.75cm in x dir (edge of probe is 7cm beyond that both ways)
    sign = -1 if dir == 0 else +1
    loc1 = (x + sign*17.75*math.cos(phirad) + 12.0*math.sin(phirad),y+12.0*math.cos(phirad) - sign*17.75*math.sin(phirad)) 
    loc2 = (x - sign*17.75*math.cos(phirad) + 12.0*math.sin(phirad),y+12.0*math.cos(phirad) + sign*17.75*math.sin(phirad))
    save_reading(data1,loc1)
    save_reading(data2,loc2)
    '''nxt_raster_dir = nxt_raster_dir==0'''
    probe.close()
    return

def extract_counts(data):
    """
    Takes the serial dump from the Ludlum probe and extracts the current
    scalar counts value.

    *Params*:
    - data: a string originating from the Ludlum data dumb

    *Returns*:
    - counts: an integer value corresponding to the scalar counts
    """
    dat = [ord(x) for x in data]
    counts = dat[4:9]
    counts.reverse()
    # Next couple lines convert the hex numbers to decimal.
    # TODO: use an established normal method for doing this conversion
    counts = reduce(lambda x,y: x+y, [ counts[i]*(255**i) for i in range(5) ])
    return counts

def save_reading(data, loc):
    """
    Takes raw data dump from Ludlum, parses and converts it, and saves it in a
    data file tagged by the location.

    ** PARAMS **
      data (bytes): the raw hex data read on the serial port
      loc (tuple of floats): Location data (could be just x,y, or x,y,bearing -
        depending on what the localization module outputs)
    """
    if type(data)==type("look up stringtype later"):
        data = extract_counts(data)
    f = open(scan_fname, "a")

    # First line of the file: give headings to the data columns
    if f.tell() == 0:
        f.write("counts,x,y\n")
    # Write the actual data values to the file
    f.write("%d,%d,%d\n" % (data, loc[0], loc[1]))
    f.close() 
    return

def save_position(locat):
    """
    """
    loc_fname = 'robot_locs.txt'
    f = open(loc_fname,"a")

    if f.tell() == 0:
        f.write(locat.keys())
        f.write('x,y,phi\n')

    return

def task_continuous_proberead():
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
        locat = localization.get_position(location)

        f = open(scan_fname, "a")
        # First line of the file: give headings to the data columns
        if f.tell() == 0:
            f.write("counts,x,y\n")
        f.write("%d,%f,%f\n" % (scalarCounts, locat[0], locat[1]))
        f.close() 
    probe.close()
    return
    
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


