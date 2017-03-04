"""Created February 2017.
This is a suite of robot localization functions that make use of the
Adafruit BNO055 inertial measurement unit (IMU). The robot's location (IMU
location) and bearing (Euler "z" angle) are stored in a dictionary for easy
updating functionality. This implementation of localization functionality is
an ADT."""

import logging
import sys
import time
import math

'''
 WILL TRY TO GET THIS WORKING LATER
from imp import load_source
path_to_loc_drivers='resources/Adafruit_Python_BNO055/'
load_source('Adafruit_BNO055', path_to_loc_drivers) 
'''
import BNO055
global bno
bno = BNO055.BNO055(serial_port='/dev/serial0', rst=18)

def locat_create(x = 0, y = 0, phi = 0):
    """Creates a new dictionary to store the location of the robot. Unless
    otherwise specified, all localization values are initialized to zero."""
    return {'x': x, 'y': y, 'phi': phi}

def IMU_initialize():
    """Set up the IMU. This is essentially just copied code from the 'simpletest.py'
    file that Adafruit provides for the IMU"""

    # Raspberry Pi configuration with serial UART and RST connected to GPIO 18:
 #   bno = BNO055.BNO055(serial_port='/dev/serial0', rst=18)
    # Enable verbose debug logging if -v is passed as a parameter.
    if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
        logging.basicConfig(level=logging.DEBUG)
    # Initialize the BNO055 and stop if something went wrong.

    num_failures = 0
    while(1):
        try:
            bno.begin()
        except RuntimeError:
            num_failures += 1
        else:
            print("Failed " + str(num_failures) + " times before bno.begin() worked.")
            break

    # Print system status and self test result.
    status, self_test, error = bno.get_system_status()
    # Print out an error if system status is in error mode.
    if status == 0x01:
        print('System error: {0}'.format(error))
        print('See datasheet section 4.3.59 for the meaning.')
    
    return

def bearing_update(locat, phi = None):
    """Updates the current bearing of the robot using the BNO055 IMU. By default,
    calling this function will initiate an IMU poll. However, if this has already
    been done, then the bearing is simply updated to reflect the result of a
    previous poll."""
    if phi is None:
        # Read the Euler angles for heading, roll, pitch (all in degrees).
        heading, roll, pitch = bno.read_euler()
        locat['phi'] = heading
    else:
        locat['phi'] = phi
    return

def position_update(locat, encL, encR, phi1, phi2):
    """Uses a simple linear scheme to compute the new position of the IMU in
    the x-y plane. One has to supply the left and right encoder counts, and the
    initial and final bearing angles (phi is assumed to be measured clockwise
    from the y-axis, which runs along the longer dimension of the trailer."""

    # For now we do an average encoder value to discern the arc length. However,
    # more complex schemes where the movement step is broken up into two linear
    # steps at different angles to account for one wheel turning more than the
    # other are possible, and we could work them out later or simply state that
    # this could be left for future iterations.
    encAve = (encL + encR)//2
    phiAve = (phi1 + phi2)/2

    # 6 cm radius wheels and 131 encoder edges per rotation yields the magic
    # number used here
    locat['x'] += math.sin(phiAve)*encAve*0.28777948
    locat['y'] += math.cos(phiAve)*encAve*0.28777948
    locat['phi'] = phi2
    
    return

def get_position(locat):
    """Reads out the location (x, y, phi) as a tuple to be consistent with other code"""
    return (locat['x'],locat['y'],locat['phi'])


