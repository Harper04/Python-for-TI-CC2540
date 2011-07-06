import serial,struct
import time

import os,sys
from threading import Thread



class keythread(Thread):
	def __init__(self):
		Thread.__init__(self)
	def run(self):
		while BTDevice().ser.isOpen():
			x=raw_input()
			if x=="d":
				BTDevice().doDiscovery()
			if x=="e":
				BTDevice().doEstablishLink(0)
			if x=="t":
				BTDevice().doTerminateLink()
			if x=="1":
				BTDevice().writeStack.append(BTDevice().activateAccelerometer)
				BTDevice().writeStack.append(BTDevice().setUpZAccNotifications)
				BTDevice().writeStack.append(BTDevice().setUpXAccNotifications)
				BTDevice().writeStack.append(BTDevice().setUpYAccNotifications)
				BTDevice().setUpButtNotifications()
			if x=="2":
				BTDevice().writeStack.append(BTDevice().deactNotificationForSensor)
				BTDevice().writeStack.append(BTDevice().deactNotificationForSensor)
				BTDevice().writeStack.append(BTDevice().deactNotificationForSensor)
				BTDevice().writeStack.append(BTDevice().deactivateAccelerometer)
				BTDevice().deactNotificationForSensor()
				
				#BTDevice().deactivateAccelerometer()
		
	def sendNextPacket(self):
		print BTDevice().writeStack
		if BTDevice().writeStack != []:
			BTDevice().writeStack.pop(0)()
		else:
			print "No Packets to send"


class BTDevice(object):
    _shared = {}
    def __init__(self):
	self.__dict__ = self._shared
    deviceReady=0
    dongleAddress="\x00\x00\x00\x00\x00\x00\x00\x00"
    IRK="\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    CSRK="\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    ser = serial.Serial()
    foundDevices = {}
    connHandle=""
    nextWriteCommand=""
    thread=keythread()
    writeStack=[]
    def doDiscovery(self):
	print "Doing Discovery"
	st='\x01' #command
	st=st+'\x04\xFE' # 0xFE GAP_DeviceDiscoveryRequest
	st=st+'\x03' # Datalength, well static ^^
	st=st+'\x03' #Mode (all)
	st=st+'\x01' #Enable Name Mode
	st=st+'\x00' #Disable Whitelist
	#self.nextWriteCommand=st
	self.ser.write(st)
    def doEstablishLink(self,device):
	print "Sending establish link request"
	st='\x01' #command
	st=st+'\x09\xfe' #0xfe09 gap_establishlinkrequest
	st=st+'\x09' #datalength
	st=st+'\x00' #Highdutycycle
	st=st+'\x00' #whitelist
	st=st+'\x00' #AddrTypePeer (our keyfob is 00)
	st=st+self.foundDevices[device]['BinAddr']
	#self.nextWriteCommand=st
	self.ser.write(st)
    def doTerminateLink(self):
	st='\x01' #command
	st=st+'\x0A\xFE' #0xFE0A GAP Terminatelinkrequest
	st=st+'\x02' #data
	st=st+str(self.connHandle) #conn handle   GetBY BLA!!!!
	#self.nextWriteCommand=st
	self.ser.write(st)
	
    #wir setzen hier nur die bewegung in gang, HCIEvents wird den rest der pakete schicken parsen etc.
    def setUpXAccNotifications(self):
	st='\x01' #command
	st=st+'\x88\xFD'   # 0xFD88 (GATT_DiscCharsByUUID)
	st=st+'\x08'		#data length
	st=st+'\x00\x00'	#connectionhandle
	st=st+'\x01\x00'	#Starting handle
	st=st+'\xFF\xFF'	#end handle
	st=st+'\xA3\xFF'	#UUID we are searching for (X)
	self.ser.write(st)
    def setUpYAccNotifications(self):
	st='\x01' #command
	st=st+'\x88\xFD'   # 0xFD88 (GATT_DiscCharsByUUID)
	st=st+'\x08'		#data length
	st=st+'\x00\x00'	#connectionhandle
	st=st+'\x01\x00'	#Starting handle
	st=st+'\xFF\xFF'	#end handle
	st=st+'\xA4\xFF'	#UUID we are searching for (Y)
	self.ser.write(st)
    def setUpZAccNotifications(self):
	st='\x01' #command
	st=st+'\x88\xFD'   # 0xFD88 (GATT_DiscCharsByUUID)
	st=st+'\x08'		#data length
	st=st+'\x00\x00'		#connectionhandle
	st=st+'\x01\x00'	#Starting handle
	st=st+'\xFF\xFF'	#end handle
	st=st+'\xA5\xFF'	#UUID we are searching for (Z)
	self.ser.write(st)
    def setUpButtNotifications(self):
	st='\x01' #command
	st=st+'\x88\xFD'   # 0xFD88 (GATT_DiscCharsByUUID)
	st=st+'\x08'		#data length
	st=st+'\x00\x00'	#connectionhandle
	st=st+'\x01\x00'	#Starting handle
	st=st+'\xFF\xFF'	#end handle
	st=st+'\xE1\xFF'	#UUID we are searching for (Button)
	self.ser.write(st)

    def activateAccelerometer(self):
	#Write Command
	st = '\x01' #command
	st = st+'\x12\xFD'   #0xFD12 (ATT_WriteReq)
	st = st+'\x07'	#datalength
	st = st+self.connHandle	#handle
	st = st+'\x00' #Signature off
	st = st+'\x00' #command off
	st = st+'\x21\x00'		#attribute Address
	st = st+'\x01'	#AttrValue
	self.ser.write(st)

    def activateAccelerometer(self):
	#Write Command
	st = '\x01' #command
	st = st+'\x12\xFD'   #0xFD12 (ATT_WriteReq)
	st = st+'\x07'	#datalength
	st = st+self.connHandle	#handle
	st = st+'\x00' #Signature off
	st = st+'\x00' #command off
	st = st+'\x21\x00'		#attribute Address
	st = st+'\x01'	#AttrValue
	self.ser.write(st)
    def deactivateAccelerometer(self):
	#Write Command
	st = '\x01' #command
	st = st+'\x12\xFD'   #0xFD12 (ATT_WriteReq)
	st = st+'\x07'	#datalength
	st = st+self.connHandle	#handle
	st = st+'\x00' #Signature off
	st = st+'\x00' #command off
	st = st+'\x21\x00'		#attribute Address
	st = st+'\x00'	#AttrValue
	self.ser.write(st)

    notificationAttributeAddresses=[]
    #notificationAttributeAddresses2=['\x28\x00','\x2C\x00','\x30\x00','\x28\x00']
    def setUpNotificationForSensor(self):
	#Write Command
	st = '\x01' #command
	st = st+'\x12\xFD'   #0xFD12 (ATT_WriteReq)
	st = st+'\x08'	#datalength
	st = st+self.connHandle	#handle
	st = st+'\x00' #Signature off
	st = st+'\x00' #command off
	#x=self.notificationAttributeAddresses2.pop()
	x=self.notificationAttributeAddresses.pop()
	self.notificationAttributeAddressesAct.append(x)
	print x
	st = st+x#'\x28\x00'		#attribute Address
	st = st+'\x01\x00'	#AttrValue
	self.ser.write(st)



    notificationAttributeAddressesAct=[]
    def deactNotificationForSensor(self):
	print sel.notificationAttributeAddressesAct
	if self.notificationAttributeAddressesAct == []:
		return
	#Write Command
	st = '\x01' #command
	st = st+'\x12\xFD'   #0xFD12 (ATT_WriteReq)
	st = st+'\x08'	#datalength
	st = st+self.connHandle	#handle
	st = st+'\x00' #Signature off
	st = st+'\x00' #command off
	x=self.notificationAttributeAddressesAct.pop()
	print x
	st = st+x#'\x28\x00'		#attribute Address
	st = st+'\x00\x00'	#AttrValue
	self.ser.write(st)
