from twisted.internet.protocol import Protocol, Factory
from struct import pack
import game.protocol
from core.packet import WGPacketReader, WGPacket

class ClientProtocol(Protocol):
    protocol = game.protocol.getProtocol("web")
    def __init__(self):
        self.player = None

    def connectionMade(self):
        try:
            # Enable TCP_NO_DELAY
            self.transport.setTcpNoDelay(True)
        except:
            # May not always work.
            pass

    def dataReceived(self, data):
        packet = WGPacketReader(data)
        
        packet = chr(1) + chr(0) + pack("!H", 3031)
        packet += chr(1) + chr(1) + chr(8) + pack("!H", len(game.item.sprites["item"]["3031"][0]))
        packet += str(game.item.sprites["item"]["3031"][0])
        self.transport.write(packet)

        packet = chr(1) + chr(0) + pack("!H", 1454)
        packet += chr(2) + chr(2) + chr(1) + pack("!H", len(game.item.sprites["item"]["1454"][0]))
        packet += str(game.item.sprites["item"]["1454"][0])
        self.transport.write(packet)

        packet = chr(1) + chr(1) + pack("!H", 27)
        packet += chr(game.item.sprites["outfit"]["27"][1][0]) + chr(game.item.sprites["outfit"]["27"][1][1]) + chr(game.item.sprites["outfit"]["27"][1][6])
        packet += pack("!H", len(game.item.sprites["outfit"]["27"][0]))
        packet += str(game.item.sprites["outfit"]["27"][0])
        self.transport.write(packet)
        
class ClientFactory(Factory):
    protocol = ClientProtocol


