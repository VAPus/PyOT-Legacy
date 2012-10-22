import protocolbase
from twisted.internet.defer import inlineCallbacks
from twisted.python import log
from packet import TibiaPacket, TibiaPacketReader
import sql
import otcrypto
import config
import socket
from struct import pack

class SimplePacket(TibiaPacket):
    def send(self, stream):
        if not stream or not self.data: return
        stream.transport.write(self.data)   

IPS = {}
class extProtocol(protocolbase.TibiaProtocol):
    def onInit(self):
        self.gotFirst = True
        self.lastResource = ""
        self.files = {}
        self.player = None
        self.ip = ""
    def dataReceived(self, data):
        packet = TibiaPacketReader(data)
        self.onPacket(packet)
    
    def onConnect(self):
        self.ip = self.transport.getPeer().host
        IPS[self.ip] = self
        
    def onPacket(self, packet):
        type = packet.uint8()
        
        if type == 0x00:
            return
        if type == 0x01:
            p = SimplePacket(0x05)
            data = self.files[self.lastResource].read()
            p.uint32(len(data))
            p.data += data
            p.send(self)
    
    def _load(self, res):
        if not res in self.files:
            if res[:4] == "data":
                self.files[res] = open(res)
        self.lastResource = res
        p = SimplePacket()
        p.uint8(0x00)
        print len(res)
        p.string(res)
        p.send(self)
        
    def play(self, res, loop=False):
        if res != self.lastResource:
            self._load(res)
            
        p = SimplePacket(0x02 if loop else 0x01)
        p.send(self)
        
    def stop(self, all=False):
        if all:
            p = SimplePacket(0x03)
        else:
            p = SimplePacket(0x02)
            
        p.send(self)
        
    def destroy(self):
        p = SimplePacket(0x04)
        p.send(self)
        
    def onConnectionLost(self):
        if self.player:
            pass
            
        del IPS[self.ip]
        
    def resource(self, res, data):
        self.files[res] = data
        
class ExtFactory(protocolbase.TibiaFactory):
    __slots__ = ()
    protocol = extProtocol

    def __repr__(self):
        return "<Ext Server Factory>"
