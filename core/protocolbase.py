from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from twisted.python import log
from packet import TibiaPacketReader, TibiaPacket
import config
from struct import unpack

if config.checkAdler32:
    from zlib import adler32
  
class TibiaProtocol(Protocol):
    #__slots__ = 'gotFirst', 'xtea', 'buffer', 'nextPacketLength', 'bufferLength'
    def __init__(self):
        self.gotFirst = False
        self.xtea = None
        self.onInit()
        self.data = []
        self.expect = 0
        self.player = None
        
    def connectionMade(self):
        peer = self.transport.getPeer()
        log.msg("Connection made from {0}:{1}".format(peer.host, peer.port))
        
        # Enable TCP_NO_DELAY
        self.transport.setTcpNoDelay(True)

        # Add self to a queue
        self.factory.addClient(self)

        # Inform the Protocol that we had a connection
        self.onConnect()

    def connectionLost(self, reason):
        peer = self.transport.getPeer()
        log.msg("Connection lost from {0}:{1}".format(peer.host, peer.port))
        self.factory.removeClient(self)
        
        # Inform the Protocol that we lost a connection
        self.onConnectionLost()

    def dataToPacket(self, data):
        if self.expect:
            if len(data) >= self.expect:
                frame = data[:self.expect]
                frame = ''.join(self.data) + frame
                self.handlePacketFrame(frame)
                self.data = []
                self.expect = 0
                
                remains = data[self.expect:]
                if remains:
                    self.dataToPacket(remains)
                
                
            else:
                self.data.append(data)
                self.expect -= len(data)
        else:
            expect = unpack("<H", data[:2])[0]
            recevied = len(data) - 2
            if recevied == expect:
                self.handlePacketFrame(data[2:])
            elif recevied > expect:
                self.handlePacketFrame(data[2:2+expect])
                self.dataToPacket(data[2+expect:])
            else:
                self.expect = expect-recevied
                self.data.append(data)  
                
    def dataReceived(self, data):
        self.dataToPacket(data)
            
        
    def handlePacketFrame(self, packetData):
        packet = TibiaPacketReader(packetData)
        # Adler32:
        if config.checkAdler32:
            adler = packet.uint32()
            calcAdler = adler32(packet.getData()) & 0xffffffff
            if adler != calcAdler:
                log.msg("Adler32 missmatch, it's %s, should be: %s" % (calcAdler, adler))
                self.transport.loseConnection()
                return
        else:
            packet.pos += 4

        if self.gotFirst:
            self.onPacket(packet)
        else:
            self.gotFirst = True
            self.onFirstPacket(packet)
        
    #### Protocol spesific, to be overwritten ####
    def onConnect(self):
        pass

    def onConnectionLost(self):
        pass

    def onFirstPacket(self, packet):
        self.onPacket(packet)

    def onPacket(self, packet):
        pass

    def onInit(self):
        pass

    #### Some simplefiers ####
    def loseConnection(self):
        self.onConnectionLost()
        reactor.callLater(1, self.transport.loseConnection) # We add a 1sec delay to the lose to prevent unfinished writtings from happending

class TibiaFactory(Factory):
    #__slots__ = 'clientCount'
    protocol = None # This HAVE to be overrided!
    def __init__(self):
        #self.clients = []
        self.clientCount = 0

    def addClient(self, client):
        #self.clients.append(client)
        self.clientCount = self.clientCount + 1
        

    def removeClient(self, client):
        #if client in self.clients:
        #    self.clients.remove(client)
        self.clientCount = self.clientCount - 1
