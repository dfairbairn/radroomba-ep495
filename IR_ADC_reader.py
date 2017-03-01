#!/usr/bin/env python

# Written by Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# This code is released into the public domain

import time
import os

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)

        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

# read value from the IR sensor
def read_IR(adc_channel, last_read):
        # Input which channel of the ADC the function should read from
        # last_read keeps track of the last potentiometer value (global variable I think)

        # change these as desired - they're the pins connected from the
        # SPI port on the ADC to the Cobbler
        SPICLK = 17
        SPIMISO = 4
        SPIMOSI = 3
        SPICS = 2

        # set up the SPI interface pins
        GPIO.setup(SPIMOSI, GPIO.OUT)
        GPIO.setup(SPIMISO, GPIO.IN)
        GPIO.setup(SPICLK, GPIO.OUT)
        GPIO.setup(SPICS, GPIO.OUT)

        wall = False
        tolerance = 5       # to keep from being jittery we'll only change
        end_tolerance = -15  # A measure of how much, the next value can drop at end of range

        # we'll assume that the distance did not change
        probe_changed = False

        # read the analog pin
        IR_probe = readadc(adc_channel, SPICLK, SPIMOSI, SPIMISO, SPICS)

        # how much has it changed since the last read?
        probe_adjust = IR_probe - last_read

        if abs(probe_adjust) > tolerance:
                probe_changed = True

                if (IR_probe > 900) or (last_read > 900):
                    if probe_adjust < end_tolerance:
                        print("A wall has been reached.")
                        wall = True

        if probe_changed:
            # save the potentiometer reading for the next loop
            new_read = IR_probe
        else:
            new_read = last_read

        return new_read, wall

last_read = 0

while True:
    result = read_IR(0, last_read) # get result for channel 0
    last_read = result[0] # Store new last_read
    print(last_read)
    print("The wall is", result[1])
    print(" ")
    time.sleep(0.25) # wait for a bit
    if result[1]: # check the wall
        print("Wall found")
        break

