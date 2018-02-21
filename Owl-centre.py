#!/usr/bin/python
###########
# sets servos to centre XY
###################
import sys # for stderr printing

# now set up the PWM server using pigpiod.if (python)
import pigpio
import time

leftXpin=16
leftYpin=14
rightXpin=17
rightYpin=15
neckpin=13

Rx = 1535
Ry = 1440
Lx = 1555
Ly = 1550
Neck = 1530

pi1 = pigpio.pi()
# set up servo ranges
pi1.set_PWM_range(leftYpin, 10000)
pi1.set_PWM_range(leftXpin, 10000)
pi1.set_PWM_range(rightYpin, 10000)
pi1.set_PWM_range(rightXpin, 10000)
pi1.set_PWM_range(neckpin, 10000)

pi1.set_PWM_frequency(leftYpin,100)
pi1.set_PWM_frequency(leftXpin,100)
pi1.set_PWM_frequency(rightYpin,100)
pi1.set_PWM_frequency(rightXpin,100)
pi1.set_PWM_frequency(neckpin,100)



# range check to prevent servo overdrive
if (Ry>2000):
	Ry = 2000
if (Ry<1120):
	Ry = 1120
if (Rx>1890):
	Rx = 1890
if (Rx<1200):
	Rx = 1200
if (Ly>2000):
	Ly = 2000
if (Ly<1180):
	Ly = 1180
if (Lx>1850):
	Lx = 1850
if (Lx<1180):
	Lx = 1180
if (Neck>1950):
	Neck=1950
if (Neck<1100):
	Neck=1100
pi1.set_PWM_dutycycle(rightYpin, Ry) #5
pi1.set_PWM_dutycycle(rightXpin, Rx) #6
pi1.set_PWM_dutycycle(leftYpin, Ly) #7
pi1.set_PWM_dutycycle(leftXpin, Lx) #8
pi1.set_PWM_dutycycle(neckpin, Neck) #9

# on exit from loop (send a "" packet)
pi1.stop()
