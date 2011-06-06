import serial
from BTDevice import BTDevice,keythread
import struct
import binascii




class HCIEvents:
	def nomatch(self,i,bt):
		print "no match found"
	
	def do_process_att_writeResponse_event(self,i,bt):
		if bt.read()=='\x00':
			print "Notification activated"
			#Writesuccess
			bt.read(3)
			BTDevice().thread.sendNextPacket()
		else:
			print "Write failed"

	def do_process_att_readbytypeResponse_event(self,laenge,bt): #we use this only for setting up notifications
		i=bt.read()
		if i=='\x1A':
			print "ATT ReadbyTypeResponse A1"
			#device is just telling me that search has ended
			#so lets read the rest
			bt.read(size=3)
			BTDevice().thread.sendNextPacket()
		elif i=='\x00':

			P=struct.unpack('<HBBH',bt.read(size=6))
			#ConnHandle PDULen DataLength Handle# Data
			Data=struct.unpack('<'+str(P[2]-2)+'B',bt.read(size=P[2]-2))
			print "LENGTH OF PDU : "+str(P[2])
			if P[2]==7:
				print str(hex(P[3]))+" found handle"
				address = struct.pack('BB',P[3]+2,0)
				print "Got Handle for sensor, setting up notification..."
				BTDevice().notificationAttributeAddresses.append(address)
				BTDevice().writeStack.append(BTDevice().setUpNotificationForSensor)
				
			
	def do_process_gap_handlevalue_notification_event(self,i,bt):
		P=struct.unpack('<BHB',bt.read(size=4))
		print "--------------------"
		print "Receive HandleValue notification from connhandle: "+str(P[1])
		
		#bla eventlength = 3 fuer test
		ii=struct.unpack('<HB',bt.read(size=3))
		print "Attribute: "+str(hex(ii[0]))+" Value: "+str(ii[1])
		#Attribute 31 ist fuer die tasten

	def do_process_gap_terminate_link_event(self,i,bt):
		P=struct.unpack('<B2sB',bt.read(size=4)) #status#connhandel#reason
		if P[0]==0:
			print "Connection closed"
			if BTDevice.connHandle==P[1]:
				BTDevice.connHandle=""
				print "Connection to Keyfob closed"
				BTDevice().ser.close()
				print "Terminating App, Please press Enter"
			
	def do_process_gap_establish_link_event(self,i,bt):
		P=struct.unpack('<BB6s2sHHHB',bt.read(size=17))
		# Status, DevAddrType DevAddr ConnHandle ConnIntervall ConnLatency ConnTimeout ClockAccuracy
		BTDevice.connHandle=P[3]
		print "Established Link connection to keyfob"

	def do_process_gap_deviceinformation_event(self,i,bt):
		P=struct.unpack('<BBB6sBB',bt.read(size=11))
		#Status EventType AddrType Addr Rssi DataLength Data
		PP= bt.read(size=P[5])
		print "Device "+binascii.b2a_hex(P[3])+" responded to discovery with "+binascii.b2a_hex(PP)+" (reverse)"

	def do_process_gap_discovery_done(self,i,bt):
		Params= struct.unpack('<BB',bt.read(size=2)) #status, NumDevices
		if Params[0]==0:
			if Params[1]==0:
				print "Devices Discovery Done, found 0 Devices"
			else:
				print "Device Discovery Done, found "+str(Params[1])+" Devices"
				dic={}
				for ii in range(Params[1]):
					P=struct.unpack('<BB6s',bt.read(size=8))
					dic[ii] = {'EvType':P[0],'AddrType':P[1],'Addr':binascii.b2a_hex(P[2]),'BinAddr':P[2]}
				print dic
				BTDevice.foundDevices=dic					
		else:
			print "Error during device Discovery"

	def do_process_gap_deviceinit_done(self,i,bt):
		print "Got Device init done"
		Params = struct.unpack('<B6sHB16s16s',bt.read(size=42))
		#Status,devAddr,dataPktLen,numDataPkts,IRK,CSRK
		if Params[0]==0: #success
			print "Device initialized and ready"
			BTDevice.dongleAddress 	= Params[1]
			print binascii.b2a_hex(BTDevice.dongleAddress)
			BTDevice.IRK		= Params[4]
			BTDevice.CSRK		= Params[5]
			BTDevice.deviceReady	= 1
		else:
			print "Init failed"
			exit()

	def do_process_gap_hci_ext_command_status(self,i,bt):
		Params = struct.unpack('<BH',bt.read(size=3))
		print Params[1]
		print Params[0]
		if Params[0]==0:
			if Params[1]== 65024: #0xFE00 GAP_deviceINIT 
				print "Dongle recieved GAP_deviveInit command"
				bt.read() # get last byte from device (Datalength unused..)
			elif Params[1] == 65028: #0xFE04 GAP Device Discovery Request
				print "Dongle recieved command and is now searching"
				bt.read()
			elif Params[1] == 65033: #0xFE09 Gap Establish link request
				print "Dongle recieved estalblish link request"
				bt.read()
			elif Params[1] == 65034: #FE0A Gap terminate linkrequest
				print "Dongle recieved link term request"
				bt.read()
			elif Params[1] == 64904: #0xFD88 (GATT_DiscCharsByUUID)
				print "Keyfob is searching"
				bt.read() #work in progress concerning our search :)
				#bt.read()
			elif Params[1] == 64786:  #0xFD12 (ATT_WriteReq)
				print "Keyfob got WriteRequest"
				bt.read()
			else:
				print "Unknown OpCode"+str(Params[1])
		else:
			print "Somethings's wrong"
			bt.read()
	def lookup(self,d):
		if d == 1536:
			bla= "do_process_gap_deviceinit_done" #0600 GAP_DeviceInitDone
		elif d == 1289: #0x0509 (ATT_ReadByTypeRsp)
			bla = "do_process_att_readbytypeResponse_event"
		elif d == 1299: #0x0513 (ATT_WriteRsp)
			bla = "do_process_att_writeResponse_event"
		elif d == 1663: #067F GAP HCI Extension Command Status
			bla = "do_process_gap_hci_ext_command_status" 
		elif d == 1537: # 0610 GAP_DeviceDiscoveryDone
			bla = "do_process_gap_discovery_done"
		elif d == 1549: # 006D GAP DeviceInformation Event
			bla = "do_process_gap_deviceinformation_event"
		elif d == 1541: #0605 Gap Establish Link
			bla = "do_process_gap_establish_link_event"
		elif d == 1542: #0606 Gap TerminateLink
			bla = "do_process_gap_terminate_link_event"
		elif d == 1307: #051b #ATT HandleValueNotification
			bla = "do_process_gap_handlevalue_notification_event"
		else:
			bla = "nomatch"
		return getattr(self, bla, None)
