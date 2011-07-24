from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from twisted.python import log
from twisted.application.service import Service
from packet import TibiaPacketReader, TibiaPacket
from zlib import adler32
import config, thread

class TibiaProtocol(Protocol):

    def __init__(self):
        self.gotFirst = False
        self.xtea = ()
        self.sendLock = thread.allocate_lock()
        self.onInit()

    def connectionMade(self):
        peer = self.transport.getPeer()
        log.msg("Connection made from {0}:{1}".format(peer.host, peer.port))
        
        # Enable TCP_NO_DELAY
        self.transport.setTcpNoDelay(True)

        # Add self to a queue
        self.factory.addClient(self)

        # Inform the Protocol that we had a connection
        self.onConnect();

    def connectionLost(self, reason):
        peer = self.transport.getPeer()
        log.msg("Connection lost from {0}:{1}".format(peer.host, peer.port))
        self.factory.removeClient(self)

        # Inform the Protocol that we lost a connection
        self.onConnectionLost()

    def dataReceived(self, data):
        packet = TibiaPacketReader(data)

        # Length
        gotLength = packet.uint16()
        if len(data)-2 != gotLength:
            log.msg("Packet length is invalid (exptected %d, got %d)" % (gotLength, len(data)-2))
            self.transport.loseConnection()
            return

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
    def exitWithError(self, message, error = 0x0A):
        packet = TibiaPacket()
        packet.uint8(error) # Error code
        packet.string(message) # Error message
        packet.send(self)
        self.loseConnection()

    def loseConnection(self):
        self.onConnectionLost()
        self.sendLock.acquire() # Yes, no new writings can happend. We might risk a deadlock here or exception in send()
        reactor.callLater(1, self.transport.loseConnection) # We add a 1sec delay to the lose to prevent unfinished writtings from happending

class TibiaFactory(Factory):
    protocol = None # This HAVE to be overrided!
    def __init__(self, service):
        self.service = service
        self.clients = []
        self.clientCount = 0
        self.idsTaken = 0

    def addClient(self, client):
        self.clients.append(client)
        self.clientCount = self.clientCount + 1
        

    def removeClient(self, client):
        if client in self.clients:
            self.clients.remove(client)
        self.clientCount = self.clientCount - 1

class TibiaService(Service):
    pass
