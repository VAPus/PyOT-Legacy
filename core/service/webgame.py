from twisted.internet.protocol import Protocol, Factory

class ClientProtocol(Protocol):
    def _delayed(self):
        self.transport.write(" NOT!")
    def dataReceived(self, data):
        self.transport.write(data)
        callLater(3, self._delayed)

class ClientFactory(Factory):
    protocol = ClientProtocol


