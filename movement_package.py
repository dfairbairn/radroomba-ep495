'''The idea behind this task is to drive the robot forward by one position increment before the task exits smoothly.
Likely, this increment is the length of the Ludlum GM probe itself, which is 12.9 cm. For some overlap I will, for now,
assume we want to move forward by 12.4 cm each time.'''

from __future__ import print_function
import sys
import time
import wiringpi
import math
import numpy
from localization import *
from dual_mc33926_rpi import motors, MAX_SPEED
from Adafruit_BNO055 import BNO055

#Python 2 is dumb and gives an error having to do with clearing the stdout buffer due to my use of a try except block.
#This bit of code will kill the error message
sys.excepthook = lambda *args: None

#ISR
'''Handles the motor encoder counter incrementing and, when the robot has moved far enough, disables the motors.'''

def encoder_ISR_L():
    #First things first, increment the left encoder
    global encoders
    encoders["left"] += 1

    #Wheels are 6 cm in radius, so it takes 0.32892 rotations to travel 12.4 cm. 131 encoder edges per rotation so
    #43.08 encoder edges to reach the desired position. Round down to 43, but every 10 increments add an extra increment
    #to keep an accurate record of total distance moved.
    if encoders["left"] % 10 == 0:
        encoders["left"] += 1

    #Did this wheel go far enough? If it did but the other wheel hasnt yet, slow the robot way down, since the other
    #wheel is likely to reach the goal *very* soon, and we want to avoid inertia-related overshooting if possible
    if encoders["left"] >= target:
        control_bools["left_limit"] = True
        #Stop the motors immediately if the target has been reached by both wheels
        if control_bools["left_limit"] and control_bools["right_limit"]:
            control_bools["far_enough"] = True
            motors.setSpeeds(0,0)
        #Slow thfrom resources/Adafruit_Python_BNO055/Adafruit_BNO055 import BNO055e motors by if we are still waiting on the right wheel
 #       else:
   #         motors.setSpeeds(MAX_SPEED/10,MAX_SPEED/10)

    #Exit the ISR
    return

def encoder_ISR_R():
    #First things first, increment the left encoder
    global encoders
    encoders["right"] += 1

    #Wheels are 6 cm in radius, so it takes 0.32892 rotations to travel 12.4 cm. 131 encoder edges per rotation so
    #43.08 encoder edges to reach the desired position. Round down to 43, but every 10 add an extra increment to keep
    #an accurate record of total distance moved.
    if encoders["right"] % 10 == 0:
        encoders["right"] += 1
   # print('R:',encoders["left"],'R',encoders["right"],'\n')
    #Did this wheel go far enough? If it did but the other wheel hasnt yet, slow the robot way down, since the other
    #wheel is likely to reach the goal *very* soon, and we want to avoid inertia-related overshooting if possible
    if encoders["right"] >= target:
        control_bools["right_limit"] = True
        #Stop the motors immediately if the target has been reached by both wheels
        if control_bools["left_limit"] and control_bools["right_limit"]:
            control_bools["far_enough"] = True
            motors.setSpeeds(0,0)
        #Slow the motors if we are still waiting on the left wheel
    #    else:
     #       motors.setSpeeds(MAX_SPEED/10,MAX_SPEED/10)

    #Exit the ISR
    return

def look_here(location,phiGoing):
    """Attempts to orient the robot so it is facing in the direction specified
    by phiGoing (measured counterclockwise from the y-axis in degrees)"""
    while phiGoing < 0:
        phiGoing = phiGoing + 360
    while phiGoing > 360:
        phiGoing = phiGoing - 360
 #   print('Starting to turn')
    rotate_speed = MAX_SPEED/6
    right_direction = False
    garbage1, garbage2, phiNow = get_position(location)

    #Enable motors but make sure they aren't moving
    motors.enable()
    motors.setSpeeds(0, 0)

    # .25 degree buffer, since we assume our step size is small
    if abs(phiNow - phiGoing) <= 0.15:
        return
    if abs(phiNow - phiGoing) <= 180:
        motors.setSpeeds(rotate_speed, -rotate_speed)
    else:
        motors.setSpeeds(-rotate_speed, rotate_speed)
    #Drive until it is determined that the robot is facing the right direction (determined by polling the IMU)
    while right_direction == False:
        time.sleep(0.005)
        phiNow, garbage1, garbage2 = bno.read_euler()
     #   print(phiNow, 'is the currect angle')
        diff = phiNow - phiGoing # could be -359.9 up to 359.9
        if diff < 0:
            diff = diff + 360
        if (diff <= 0.15) or (abs(diff - 360.0)<= 0.15):
            motors.setSpeeds(0,0)
            motors.disable()
            right_direction = True
        if diff > 180:
            motors.setSpeeds(rotate_speed,-rotate_speed)
        elif diff <= 180:
            motors.setSpeeds(-rotate_speed,rotate_speed)

    bearing_update(location, phiNow)
    return
        
    

def move_here(location,destination):
    """Attempts to move the robot to a specified destination along the shortest
    possible path (a straight line). Destination is just a tuple containing an
    x and a y"""

    deltaX = destination[0] - location['x']
    deltaY = destination[1] - location['y']

    arc_length = math.sqrt(deltaX**2 + deltaY**2)
    
    #Encoder target (set to be 1 lower than what we ACTUALLY want, as inertia tends to carry the wheels a bit)
    global target
    target = round(arc_length*3.474882924)
#    print('Target is ',target)

    #Determine the angle the robot must face, and call a function which will rotate the robot in the event
    #that it is not facing that direction already
    destin_angle = math.atan2(deltaX,deltaY)*180/3.1415926535
    look_here(location, destin_angle)
 #   print('Trying to advance.')
    try:
        #Can tweak as neccesary (the number to divide MAX_SPEED by determines the duty cycle and must be greater than 1)
        drive_speed = MAX_SPEED//3

        #Initial angle
        phi1 = location['phi']

        #Creating a dictionary (since dictionaries are mutable and so can be modified in functions like, say, the interrupt)
        #to store the encoder values for both wheels. Later on this *will* be moved into the master task initialization
        #routine
        global encoders
        encoders = {"left": 0, "right": 0}

        #I am going to call the variable indicating when the robot has moved far enough 'far_enough' (to be set true in the
        #encoder interrupt function)
        global control_bools
        control_bools = {"far_enough": False, "left_limit": False, "right_limit": False}

        #Enable motors but make sure they aren't moving
        motors.enable()
        motors.setSpeeds(0, 0)
        #Enable interrupt service routines for both left and right wheels (pins can be changed to whatever pins we actually use)
        wiringpi.wiringPiISR(20, 2, encoder_ISR_L)
        wiringpi.wiringPiISR(21, 2, encoder_ISR_R)

        #Drive until it is determined that the wheels have moved the appropriate distance. The interrupts will handle speed
        #adjustments as the bot approaches the desired distance
        motors.setSpeeds(drive_speed, drive_speed)
        while not control_bools["far_enough"]:
            time.sleep(0.005)
            pass

            #Update the position of the robot somehow here using the encoder values and likely the IMU as well. If there is an
            #orientation problem, this could be remedied here by calling some sort of realignment task that driven the wheels
            #very very slowly in opposite directions until the encoder values are balanced again (this would have to use new
            #encoder ISRs that could both increment and decrement the values depending on the motor speed, and then check for
            #similarity between the two encoder values). For now, since the goal is to simply move in a straight line and take
            #scans, I will hold off on implementing this.

        #Make sure the motors are off before the task exits gracefully (they are also dispabled in the ISR, but this is done
        #here for extra safety)
        motors.setSpeeds(0, 0)
        motors.disable()

        # Update position using the linear update scheme
        phi2, garbage1, garbage2 = bno.read_euler()
        position_update(location, encoders['left'], encoders['right'], phi1, phi2)
        print(encoders["left"],encoders["right"])
        print(((encoders["left"]+encoders["right"])/2)*0.28777948)
        get_position()
        #time.sleep(0.5)
    except:
        motors.setSpeeds(0, 0)
        motors.disable()
    finally:
        motors.setSpeeds(0, 0)
        motors.disable()
    return

def stop():
    motors.setSpeeds(0, 0)
    motors.disable()

if __name__ == '__main__':
    locat = locat_create()
    IMU_initialize()
    move_here(locat,(0,25))

    


