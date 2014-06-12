#Main
import serial
from HCIEvents import HCIEvents
from BTDevice import BTDevice,keythread
import struct

import os,sys
from threading import Thread

def initserial():
	bt = serial.Serial()
	if os.name == 'posix':
		bt.port = "/dev/ttyACM0"
	else:
		bt.port = "COM3"
	bt.baudrate = 57600
	bt.open()
	return bt

def initdevice(bt):
	str = '\x01' #command
	str = str+'\x00\xFE' #GAP_DeviceInit
	str = str+struct.pack('B',struct.calcsize('BB16s16sL'))+struct.pack('BB16s16sL',8,3,'\x00','\x00',1) #ProfileRole,MaxScanRsp,IRK,CSRK,SignCounter
	bt.write(str)
	print "Sent device init command!"

bt = initserial()
dev = BTDevice(bt)
print("Connected to Dongle")
initdevice(bt)
print ""
print("Starting Read loop")


#useless key thread :)

thr = keythread(dev)
thr.start()
dev.thread=thr
#

while(bt.isOpen()):  #Neues DatenPAKET wird gelesen
	HCI_Packet_Type = bt.read()
	print("\t======================")
	if HCI_Packet_Type == '\x04':	#verzweigungen... hier event
		EVENT_CODE=bt.read()
		if EVENT_CODE=='\xFF':
			print "\tFound Vendor Specific Event Code"
			X=bt.read(size=3)#enthaelt auch opcode
			DATA_LENGTH = struct.unpack('<BH',X)
			print "\tData length :"+str(DATA_LENGTH[0]) + " Data Code :"+str(DATA_LENGTH[1])
			HCIEvents().lookup(DATA_LENGTH[1])(DATA_LENGTH[0],bt,dev)

		else:
			print "*** WHAT!?! SHOULDNT HAPPEN!!!! ***"
	else:
		print struct.unpack('<B',HCI_Packet_Type)
		print "*** broken! ***"
	#if BTDevice != "":
	#	bt.write(BTDevice.nextWriteCommand)
	#	BTDevice.nextWriteCommand=""
