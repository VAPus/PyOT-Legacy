from twisted.internet.protocol import Protocol, Factory
from struct import pack

class ClientProtocol(Protocol):
    def dataReceived(self, data):
        code = "$('#log').append('Hello world from PyOT!');"
        self.transport.write(chr(0) + pack("!H", len(code)) + code)
        
        packet = chr(1) + chr(0) + pack("!H", 3031)
        packet += chr(8) + pack("!H", len(game.item.sprites["item"]["3031"][0]))
        packet += str(game.item.sprites["item"]["3031"][0])
        self.transport.write(packet)
        
class ClientFactory(Factory):
    protocol = ClientProtocol


