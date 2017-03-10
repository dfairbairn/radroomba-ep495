"""
file: 'dual_mc33926_rpi_4raster.py'
description: Adapted code for using the stepper motor controller with a RPi.
            Uses the correct GPIO pins for our CurieUS/Radroomba project!
author: Dan McCloskey
date: Feb 2017

"""
import wiringpi

# Motor speeds for this library are specified as numbers
# between -MAX_SPEED and MAX_SPEED, inclusive.
#  19.2 MHz / 40 / 1440 = 333.33333 Hz

io_initialized_stepper = False
def io_init():
  global io_initialized_stepper
  if io_initialized_stepper:
    return

 # wiringpi.wiringPiSetupGpio()
  wiringpi.pinMode(10, wiringpi.GPIO.OUTPUT)
  wiringpi.pinMode(9, wiringpi.GPIO.OUTPUT)
  wiringpi.pinMode(11, wiringpi.GPIO.OUTPUT)

  io_initialized_stepper = True

class stepMotor(object):

    def __init__(self, sqr_pin, dir_pin, en_pin):
        self.sqr_pin = sqr_pin
        self.dir_pin = dir_pin
        self.en_pin = en_pin

    def enable(self):
        io_init()
        wiringpi.digitalWrite(self.en_pin, 0)

    def disable(self):
        io_init()
        wiringpi.digitalWrite(self.en_pin, 1)

    def setDirection(self, dir):
        io_init()
        wiringpi.digitalWrite(self.dir_pin,dir)

    def toggleSquare(self, state):
        io_init()
        wiringpi.digitalWrite(self.sqr_pin,state)

''' Import the 'motor' below '''
motor = stepMotor(10, 9, 11)
