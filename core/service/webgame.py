from twisted.internet.protocol import Protocol, Factory

class ClientProtocol(Protocol):
    def dataReceived(self, data):
        self.transport.write(data)

class ClientFactory(Factory):
    protocol = ClientProtocol


