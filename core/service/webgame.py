from twisted.internet.protocol import Protocol, Factory
from struct import pack

class ClientProtocol(Protocol):
    def dataReceived(self, data):
        self.transport.write(chr(0) + pack("!H", 5) + "Hello")
        
class ClientFactory(Factory):
    protocol = ClientProtocol


