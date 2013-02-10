from twisted.internet.protocol import Protocol, Factory
from struct import pack

class ClientProtocol(Protocol):
    def dataReceived(self, data):
        code = "$('#log').append('Hello world from PyOT!');"
        self.transport.write(chr(0) + pack("!H", len(code)) + code)
        
class ClientFactory(Factory):
    protocol = ClientProtocol


