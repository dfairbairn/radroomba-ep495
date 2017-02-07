import wiringpi

# Motor speeds for this library are specified as numbers
# between -MAX_SPEED and MAX_SPEED, inclusive.
#  19.2 MHz / 40 / 1440 = 333.33333 Hz

io_initialized_stepper = False
def io_init():
  global io_initialized_stepper
  if io_initialized_stepper:
    return

  wiringpi.wiringPiSetupGpio()
  wiringpi.pinMode(10, wiringpi.GPIO.OUTPUT)
  wiringpi.pinMode(9, wiringpi.GPIO.OUTPUT)
  wiringpi.pinMode(11, wiringpi.GPIO.OUTPUT)

  io_initialized_stepper = True

class Motor(object):

    def __init__(self, sqr_pin, dir_pin, en_pin):
        self.sqr_pin = sqr_pin
        self.dir_pin = dir_pin
        self.en_pin = en_pin

    def enable(self):
        io_init()
        wiringpi.digitalWrite(self.en_pin, 1)

    def disable(self):
        io_init()
        wiringpi.digitalWrite(self.en_pin, 0)

    def setDirection(self, dir):
        io_init()
        wiringpi.digitalWrite(self.dir_pin,dir)

    def toggleSquare(self, state):
        io_init()
        wiringpi.digitalWrite(self.sqr_pin,state)

motor = Motor(10, 9, 11)
