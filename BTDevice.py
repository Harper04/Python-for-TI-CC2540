import serial,struct,binascii
import time

import os,sys
from threading import Thread


class keythread(Thread):
	def __init__(self,dev):
		self.BTDev=dev
		Thread.__init__(self)
	def run(self):
		while self.BTDev.ser.isOpen():
			x=raw_input()
			if x=="d":
				self.BTDev.doDiscovery()
			if x=="e" and self.BTDev.foundDevices!={}:
				self.BTDev.doEstablishLink(0)
			if x=="t" and self.BTDev.connHandle!="":
				self.BTDev.doTerminateLink()
			if x=="1":
				self.BTDev.writeStack.append(self.BTDev.activateAccelerometer)
				self.BTDev.writeStack.append(self.BTDev.setUpZAccNotifications)
				self.BTDev.writeStack.append(self.BTDev.setUpXAccNotifications)
				self.BTDev.writeStack.append(self.BTDev.setUpYAccNotifications)
				self.BTDev.setUpButtNotifications()
			if x=="2":
				self.BTDev.writeStack.append(self.BTDev.deactNotificationForSensor)
				self.BTDev.writeStack.append(self.BTDev.deactNotificationForSensor)
				self.BTDev.writeStack.append(self.BTDev.deactNotificationForSensor)
				self.BTDev.writeStack.append(self.BTDev.deactivateAccelerometer)
				self.BTDev.deactNotificationForSensor()
			if len(x)>1:
				if x[0]=="c" and len(x)==6: # c UUID with UUID=192A for 2A19
					self.BTDev.discCharsByUUID(x[2:])
				if x[0]=="r" and len(x)==6: # c handle with handle=2200 for 0x0022
					self.BTDev.readCharValue(x[2:])
				if x[0]=="w": # w handle value [values] with handle=2200 for 0x0022
					args = x.split()[1:]
					if len(args)>1:
						self.BTDev.writeReq(args[0],args[1:])
					else:
						print "Requires at least one value, e.g., w 2200 7"

	def sendNextPacket(self):
		print self.BTDev.writeStack
		if self.BTDev.writeStack != []:
			self.BTDev.writeStack.pop(0)()
		else:
			print "No Packets to send"


class BTDevice(object):
	_shared = {}
	def __init__(self,ser):
		self.__dict__ = self._shared
		self.ser = ser
	deviceReady=0
	dongleAddress="\x00\x00\x00\x00\x00\x00\x00\x00"
	IRK="\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
	CSRK="\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
	foundDevices={}
	connHandle=""
	thread=Thread()
	writeStack=[]
	def doDiscovery(self):
		print "Doing Discovery"
		st='\x01' #command
		st=st+'\x04\xFE' # 0xFE GAP_DeviceDiscoveryRequest
		st=st+'\x03' # Datalength, well static ^^
		st=st+'\x03' #Mode (all)
		st=st+'\x01' #Enable Name Mode
		st=st+'\x00' #Disable Whitelist
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
		self.ser.write(st)
	def doTerminateLink(self):
		print "Sending terminate link request"
		st='\x01' #command
		st=st+'\x0A\xFE' #0xFE0A GAP Terminatelinkrequest
		st=st+'\x02' #data
		st=st+str(self.connHandle) #conn handle   GetBY BLA!!!!
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

	def discCharsByUUID(self,UUID):
		st='\x01' #command
		st=st+'\x88\xFD'   # 0xFD88 (GATT_DiscCharsByUUID)
		st=st+'\x08'		#data length
		st=st+'\x00\x00'	#connectionhandle
		st=st+'\x01\x00'	#Starting handle
		st=st+'\xFF\xFF'	#end handle
		st=st+binascii.a2b_hex(UUID)	#UUID we are searching for
		self.ser.write(st)

	def writeReq(self,handle,value):
		#Write Command
		st = '\x01' #command
		st = st+'\x12\xFD'   #0xFD12 (ATT_WriteReq)
		st = st+chr(6+len(value))	#datalength
		st = st+self.connHandle	#handle
		st = st+'\x00' #Signature off
		st = st+'\x00' #command off
		st = st+binascii.a2b_hex(handle)	#attribute Address
		for i in value:
			st = st+struct.pack('B',int(i))	#AttrValue
		self.ser.write(st)

	def readCharValue(self,handle):
		st='\x01' #command
		st=st+'\x8A\xFD'   # 0xFD88 (GATT_ReadCharValue)
		st=st+'\x04'		#data length
		st=st+'\x00\x00'	#connectionhandle
		st=st+binascii.a2b_hex(handle)	#handle we are searching for
		self.ser.write(st)

	def activateAccelerometer(self):
		#Write Command
		st = '\x01' #command
		st = st+'\x12\xFD'   #0xFD12 (ATT_WriteReq)
		st = st+'\x07'	#datalength
		st = st+self.connHandle	#handle
		st = st+'\x00' #Signature off
		st = st+'\x00' #command off
		st = st+'\x33\x00'		#CHANGED from \x21\x00! attribute Address
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
		st = st+'\x33\x00'		#attribute Address
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
		print self.notificationAttributeAddressesAct
		if self.notificationAttributeAddressesAct == []:
			self.thread.sendNextPacket()
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
