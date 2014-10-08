from tornado.tcpserver import *
from packet import TibiaPacketReader
import config
from struct import unpack
import socket

if config.checkAdler32:
    from zlib import adler32
  
class TibiaProtocol:
    #__slots__ = 'gotFirst', 'xtea', 'buffer', 'nextPacketLength', 'bufferLength'
    enableTcpNoDelay = False
    def __init__(self, stream, address, server):
        self.transport = stream
        self.address = address
        self.server = server
        self.gotFirst = False
        self.xtea = None
        self.onInit()
        self.data = []
        self.expect = 0
        self.player = None
        
        # Register disconnect callback.
        self.transport.set_close_callback(self.connectionLost)
        
        self.connectionMade()
        
        # Handle reading.
        self.transport.read_until_close(self.connectionLost, self.handlePacketFrame)
        
    def connectionMade(self):
        print("Connection made from {0}".format(self.address))
        
        # Enable TCP_NO_DELAY
        self.transport.socket.setsockopt(socket.IPPROTO_TCP, socket.SO_KEEPALIVE, 1)
        self.transport.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                
        # Inform the Protocol that we had a connection
        self.onConnect()

    def connectionLost(self, reason=None):
        print("Connection lost from {0}".format(self.address))
        
        # Inform the Protocol that we lost a connection
        self.onConnectionLost()

    def dataToPacket(self, data):
        if self.expect:
            if len(data) >= self.expect:
                frame = "%s%s" % (''.join(self.data), data[:self.expect])
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
                
    def _handle_read(self, data):
        self.dataToPacket(data)
            
        
    def handlePacketFrame(self, packetData):
        # XXX: Kill first two bytes in dataToPacket.
        packet = TibiaPacketReader(packetData[2:])
        # Adler32:
        if config.checkAdler32:
            adler = packet.uint32()
            calcAdler = adler32(packet.getData()) & 0xffffffff
            if adler != calcAdler:
                print("Adler32 missmatch, it's %s, should be: %s" % (calcAdler, adler))
                self.transport.close()
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
        call_later(1, self.transport.close) # We add a 1sec delay to the lose to prevent unfinished writtings from happending

class TibiaFactory(TCPServer):
    #__slots__ = 'clientCount'
    protocol = None # This HAVE to be overrided!

    def handle_stream(self, stream, address):
        """Called when new IOStream object is ready for usage"""
        self.protocol(stream, address, self)