import time
import serial
from struct import *

# Serial Connection configuration
probe = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)

'''probe.open()'''

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
