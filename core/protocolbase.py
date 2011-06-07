from twisted.internet.protocol import Protocol, Factory
from twisted.internet.threads import deferToThread
from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor
from twisted.python import log
from twisted.application.service import Service
from core.packet import TibiaPacketReader, TibiaPacket
from zlib import adler32

class TibiaProtocol(Protocol):

    def __init__(self):
        self.client_id = 0
        self.gotFirst = False
        self.position = (70,70,7)
        self.xtea = ()
        
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
        if len(data)-2 is not packet.uint16():
            log.msg("Packet length is invalid")
            self.transport.loseConnection()
            return

        # Adler32:
        adler = packet.uint32()
        calcAdler = adler32(packet.getData()) & 0xffffffff
        if adler != calcAdler:
            log.msg("Adler32 missmatch, it's %s, should be: %s" % (calcAdler, adler))
            self.transport.loseConnection()
            return

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

    def onFirstPacket(self):
        self.onPacket()

    def onPacket(self, packet):
        pass

    def onInit(self):
        pass

    #### Some simplefiers ####
    @inlineCallbacks
    def exitWithError(self, message, error = 0x0A):
        packet = TibiaPacket()
        packet.uint8(error) # Error code
        packet.string(message) # Error message
        yield packet.send(self)
        self.loseConnection()

    def loseConnection(self):
        reactor.callLater(1, self.transport.loseConnection) # We add a 1sec delay to the lose to prevent unfinished writtings to happend

class TibiaFactory(Factory):
    protocol = None # This HAVE to be overrided!
    def __init__(self, service):
        self.service = service
        self.clients = {}
        self.clientCount = 0
        self.idsTaken = 0

    def addClient(self, client):
        client.client_id = self.generateClientID()
        self.clients[client.client_id] = client
        self.clientCount = self.clientCount + 1
        
    def generateClientID(self):
        self.idsTaken = self.idsTaken + 1
        return 0x40000001 + self.idsTaken

    def removeClient(self, client):
        if client.client_id in self.clients:
            del self.clients[client.client_id]
        self.clientCount = self.clientCount - 1

class TibiaService(Service):
    pass
