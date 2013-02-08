from twisted.internet.protocol import Protocol, Factory
from struct import pack

class ClientProtocol(Protocol):
    def dataReceived(self, data):
        self.transport.write(chr(100) + pack('!H', 1000))
        
class ClientFactory(Factory):
    protocol = ClientProtocol


