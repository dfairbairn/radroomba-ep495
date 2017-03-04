'''
file: 'move_one_increment_fancy.py'
description:
    The idea behind this task is to drive the robot forward by one position 
    increment before the task exits smoothly. Likely, this increment is the 
    length of the Ludlum GM probe itself, which is 12.9 cm. For some overlap 
    I will, for now, assume we want to move forward by 12.4 cm each time.


'''




from __future__ import print_function
import sys
import time
import wiringpi
from dual_mc33926_rpi import motors, MAX_SPEED

#Python 2 is dumb and gives an error having to do with clearing the stdout buffer due to my use of a try except block.
#This bit of code will kill the error message
sys.excepthook = lambda *args: None

#ISR
'''Handles the motor encoder counter incrementing and, when the robot has moved far enough, disables the motors.'''
#control_bools,encoders,encoders_prev, target
def encoder_ISR_L():

    #First things first, increment the left encoder
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
        #Slow the motors by if we are still waiting on the right wheel
        else:
            motors.setSpeeds(MAX_SPEED/10,MAX_SPEED/10)

    #Exit the ISR
    return
#control_bools,encoders,encoders_prev, target
def encoder_ISR_R():

    #First things first, increment the left encoder
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
        else:
            motors.setSpeeds(MAX_SPEED/10,MAX_SPEED/10)

    #Exit the ISR
    return

#This will be a global variable later on
location = {"x": 0, "y": 0}
A = True

try:

    #Can tweak as neccesary (the number to divide MAX_SPEED by determines the duty cycle and must be greater than 1)
    drive_speed = MAX_SPEED/3

    #Encoder target (set to be 1 lower than what we ACTUALLY want, as inertia tends to carry the wheels a bit)
    target = 43

    #Creating a dictionary (since dictionaries are mutable and so can be modified in functions like, say, the interrupt)
    #to store the encoder values for both wheels. Later on this *will* be moved into the master task initialization
    #routine
    encoders = {"left": 0, "right": 0}

    #I am going to call the variable indicating when the robot has moved far enough 'far_enough' (to be set true in the
    #encoder interrupt function)
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
        pass

        #Update the position of the robot somehow here using the encoder values and likely the IMU as well. If there is an
        #orientation problem, this could be remedied here by calling some sort of realignment task that driven the wheels
        #very very slowly in opposite directions until the encoder values are balanced again (this would have to use new
        #encoder ISRs that could both increment and decrement the values depending on the motor speed, and then check for
        #similarity between the two encoder values). For now, since the goal is to simply move in a straight line and take
        #scans, I will hold off on implementing this.

        #Update position (basic test case thing)
    location["y"] += ((encoders["left"]+encoders["right"])/2)*0.28777948


    #Make sure the motors are off before the task exits gracefully (they are also dispabled in the ISR, but this is done
    #here for extra safety)
    motors.setSpeeds(0, 0)
    motors.disable()

    print(encoders["left"],encoders["right"])
    print(((encoders["left"]+encoders["right"])/2)*0.28777948)
    time.sleep(0.75)
        #Disable wheel encoder interrupts (should we actually do this??? I dunno. We'll see.)
    #    wiringpi.wiringPiISR(20, 3, void)
    #    wiringpi.wiringPiISR(21, 3, void)
except:
    motors.setSpeeds(0,0)
    motors.disable()
    
finally:
    motors.setSpeeds(0, 0)
    motors.disable()




    


