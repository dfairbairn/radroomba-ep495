"""
file: 'sweep_raster.py'
date: February 2017
description:

author: David Fairbairn
        Daniel McCloskey

"""

from __future__ import print_function
import time
import wiringpi
from dual_mc33926_rpi_4raster import motor

def sweep_once(speed):
    """
    This function exists so that a single sweep of the raster scanner can be
    requested at a given speed. 

    *DOES NOT DEIGN TO DO READINGS*
    (maybe just for if scanner gets stuck or is on the wrong side)
    """

if __name__=="__main__":
    """ Original raster sweep code written by Dan """
    # Pins are in the order of: PWM, DIR, EN. I chose three somewhat at random, 
    # we can change this later.
    
    # Stepper speed specified in the module file. We want roughly 10 cm/s right 
    # now, so assuming the pulley has 30 teeth and our belt grooves are 2mm apart,
    # that means one full rotation = 6cm of travel distance. 
    # We want 10 cm/s = 1.666667 rotations per second. Our motor steps at 1.8 deg 
    # (0.005 rotations per step). Thus, we will need to drive the motor at 333.33..
    # steps per second. The stepper indexer is incremented on each rising edge  of 
    # the STEP input, so the raw PWM frequency we need is in fact 333.33333... Hz.
    
    #Initial direction
    direction = 1
    
    #Infinite loop for testing purposes (speed of 20 means 50% duty cycle)
    try:
        state = 0
        while True:
            motor.enable()
            if direction == 0:
                print("Going one way")
            elif direction == 1:
                print("Coming back")
    
    
            #34.4 cm so sleep for 3.44 seconds until scanner reaches opposite edge 
            # of the rail. Need 1147 steps total (can adjust this later)
            for half_step in range(2291):
                motor.toggleSquare(state)
                state = 1-state
                wiringpi.delayMicroseconds(1500)
    
            motor.disable()
    	    direction = 1-direction
            motor.setDirection(direction)
            time.sleep(1)
            #Wait till return key pressed
            #wait = input("Press enter when you want to go again. CTRL-C to stop.")
    
    
    finally:
        # Stop the motors, even if there is an exception
        # or the user presses Ctrl+C to kill the process.
        motor.disable()
