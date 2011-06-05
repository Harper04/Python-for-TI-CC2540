import serial,struct
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
