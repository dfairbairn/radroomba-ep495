import sys
import time
import wiringpi
from localization import *
from hwdrivers.dual_mc33926_rpi import motors, MAX_SPEED

#from Adafruit_BNO055 import BNO055
wiringpi.wiringPiSetupGpio()

#Python 2 is dumb and gives an error having to do with clearing the stdout buffer due to my use of a try except block.
#This bit of code will kill the error message
sys.excepthook = lambda *args: None

global encoders
encoders = {'left': 0,'right': 0}

#ISR
'''Handles the motor encoder counter incrementing and, when the robot has moved far enough, disables the motors.'''

global target
target = 10000
def encoder_ISR_L():
    #First things first, increment the left encoder
    #global encoders
    encoders["left"] += 1
 #   print(encoders)
 #   print()
    #Wheels are 6 cm in radius, so it takes 0.32892 rotations to travel 12.4 cm. 131 encoder edges per rotation so
    #43.08 encoder edges to reach the desired position. Round down to 43, but every 10 increments add an extra increment
    #to keep an accurate record of total distance moved.
   # if encoders["left"] % 10 == 0:
   #     encoders["left"] += 1

    #Did this wheel go far enough? If it did but the other wheel hasnt yet, slow the robot way down, since the other
    #wheel is likely to reach the goal *very* soon, and we want to avoid inertia-related overshooting if possible
    if encoders["left"] >= target:
        control_bools["left_limit"] = True
        #Stop the motors immediately if the target has been reached by both wheels
        if control_bools["left_limit"] and control_bools["right_limit"]:
            control_bools["far_enough"] = True
            motors.setSpeeds(0,0)
        #Slow thfrom resources/Adafruit_Python_BNO055/Adafruit_BNO055 import BNO055e motors by if we are still waiting on the right wheel
    #     else:
    #         motors.setSpeeds(MAX_SPEED/10,MAX_SPEED/10)

    #Exit the ISR
    return

def encoder_ISR_R():
    #First things first, increment the left encoder
 #   global encoders
    encoders["right"] += 1
  #  print(encoders)
  #  print()
    #Wheels are 6 cm in radius, so it takes 0.32892 rotations to travel 12.4 cm. 131 encoder edges per rotation so
    #43.08 encoder edges to reach the desired position. Round down to 43, but every 10 add an extra increment to keep
    #an accurate record of total distance moved.
#    if encoders["right"] % 10 == 0:
#        encoders["right"] += 1
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






def move_forward(num_encoder_ticks):
    """

    """        
    global target
    target = num_encoder_ticks
 
