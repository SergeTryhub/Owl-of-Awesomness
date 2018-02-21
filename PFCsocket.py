#!/usr/bin/python
###########
# PFC OCt 2016 basic Owl controller using IP sockets at address 10.0.0.10:12345
# socket code from https://docs.python.org/2/howto/sockets.html
###################
import socket
import sys # for stderr printing

#set the socket comms up, use TCP as it is error correcting end to end.
soc = socket.socket()
host = '10.0.0.10' #ip of raspberry pi
port = 12345
#soc.bind((host, port))

# now set up the PWM server using pigpiod.if (python)
import pigpio
import time

pi1 = pigpio.pi()
# set up servo ranges
pi1.set_PWM_range(16, 10000)
pi1.set_PWM_range(14, 10000)
pi1.set_PWM_range(17, 10000)
pi1.set_PWM_range(15, 10000)
pi1.set_PWM_range(13, 10000)

pi1.set_PWM_frequency(16,100)
pi1.set_PWM_frequency(14,100)
pi1.set_PWM_frequency(17,100)
pi1.set_PWM_frequency(15,100)
pi1.set_PWM_frequency(13,100)

#############################
# now run the server loop
#############################
soc.listen(5)
comm, addr = soc.accept()
while True:
  packet = []
  packet=comm.recv(24) # max length of 5 ints between 1200-2000 each
  comm.send('ok')
  if len(packet) < 24:
    print >> sys.stderr, 'received NULL packet, quitting'
    break
  #packet sent is Rx Ry Lx Ly N
  A = map(int, packet.split(' '))
  #A=[int(item) for item in packet.split() if item.isdigit()]
  print >> sys.stderr, A

  #Get Data from Fields
  Rx = int(A[0])
  Ry = int(A[1])
  Lx = int(A[2])
  Ly = int(A[3])
  Neck = int(A[4])
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
  pi1.set_PWM_dutycycle(16, Ry)
  pi1.set_PWM_dutycycle(14, Rx)
  pi1.set_PWM_dutycycle(17, Ly)
  pi1.set_PWM_dutycycle(15, Lx)
  pi1.set_PWM_dutycycle(13, Neck)

# on exit from loop (send a "" packet)
comm.close()
pi1.stop()
